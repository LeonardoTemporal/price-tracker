"""
Router de Productos - Endpoints para gestion de productos

Este modulo proporciona endpoints REST para listar, crear, actualizar,
eliminar y rastrear productos. Incluye soporte para scraping de precios
y generacion de alertas.

Rate limiting puede activarse descomentando el middleware correspondiente.
"""
from fastapi import APIRouter, HTTPException, status
from typing import List
import sys
import os
import logging

# Configurar logger para este modulo
logger = logging.getLogger(__name__)

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from src.tracker import Tracker
from backend.app.schemas import (
    Producto, ProductoCreate, ProductoUpdate, ProductoDetalle,
    TestURLRequest, TestURLResponse, ActualizarPrecioResponse,
    EstadisticasResponse
)

router = APIRouter()
tracker = Tracker()

# NOTE: Rate limiting puede activarse con SlowApi o fastapi-limiter
# from slowapi import Limiter, _rate_limit_exceeded_handler
# from slowapi.util import get_remote_address
# limiter = Limiter(key_func=get_remote_address)


@router.get("/", response_model=List[Producto])
async def listar_productos(activos_solo: bool = True):
    """
    Obtiene la lista de todos los productos registrados.

    Args:
        activos_solo: Si es True, incluye solo productos activos.

    Returns:
        Lista de productos con informacion resumida.

    Raises:
        HTTPException: 500 si ocurre un error interno.
    """
    try:
        resumen = tracker.obtener_resumen_productos()

        if activos_solo:
            resumen = [p for p in resumen if p.get('alerta', False) or True]

        productos = []
        for p in resumen:
            productos.append(Producto(
                id=p['id'],
                nombre=p['nombre'],
                url=p['url'],
                precio_objetivo=p['precio_objetivo'],
                activo=True,
                fecha_creacion=p['fecha_creacion'],
                precio_actual=p['precio_actual'],
                precio_min=p['precio_min'],
                precio_max=p['precio_max'],
                num_registros=p['num_registros'],
                alerta=p['alerta']
            ))

        return productos
    except Exception as e:
        logger.error(f"Error al listar productos: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{producto_id}", response_model=ProductoDetalle)
async def obtener_producto(producto_id: int):
    """
    Obtiene los detalles de un producto especifico con su historial.

    Args:
        producto_id: ID numerico del producto.

    Returns:
        ProductoDetalle con informacion completa e historial de precios.

    Raises:
        HTTPException: 404 si el producto no existe, 500 en error interno.
    """
    try:
        producto_data = tracker.db.obtener_producto(producto_id)

        if not producto_data:
            raise HTTPException(status_code=404, detail="Producto no encontrado")

        id, nombre, url, precio_objetivo, activo, fecha_creacion = producto_data

        # Obtener historial
        historial_raw = tracker.db.obtener_historial(producto_id)
        historial = [{"fecha": fecha, "precio": precio} for fecha, precio in historial_raw]

        # Estadisticas
        ultimo_precio = tracker.db.obtener_ultimo_precio(producto_id)
        precios = [precio for _, precio in historial_raw]
        precio_min = min(precios) if precios else None
        precio_max = max(precios) if precios else None

        alerta = False
        if precio_objetivo and ultimo_precio and ultimo_precio <= precio_objetivo:
            alerta = True

        return ProductoDetalle(
            id=id,
            nombre=nombre,
            url=url,
            precio_objetivo=precio_objetivo,
            activo=activo,
            fecha_creacion=fecha_creacion,
            precio_actual=ultimo_precio,
            precio_min=precio_min,
            precio_max=precio_max,
            num_registros=len(historial),
            alerta=alerta,
            historial=historial
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener producto {producto_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", response_model=Producto, status_code=status.HTTP_201_CREATED)
async def crear_producto(producto: ProductoCreate):
    """
    Crea un nuevo producto y obtiene su precio inicial.

    Args:
        producto: Datos del producto a crear (nombre, url, precio_objetivo opcional).

    Returns:
        Producto creado con precio actual obtenido via scraping.

    Raises:
        HTTPException: 400 si falla la creacion o el scraping, 500 en error interno.
    """
    try:
        resultado = await tracker.agregar_producto(
            nombre=producto.nombre,
            url=producto.url,
            precio_objetivo=producto.precio_objetivo
        )

        if not resultado['exito']:
            raise HTTPException(status_code=400, detail=resultado['mensaje'])

        # Obtener el producto completo
        producto_id = resultado['producto_id']
        producto_detalle = await obtener_producto(producto_id)

        return producto_detalle
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al crear producto: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{producto_id}", response_model=Producto)
async def actualizar_producto(producto_id: int, producto: ProductoUpdate):
    """
    Actualiza la informacion de un producto existente.

    Args:
        producto_id: ID del producto a actualizar.
        producto: Campos a actualizar (nombre, precio_objetivo, activo).

    Returns:
        Producto actualizado.

    Raises:
        HTTPException: 404 si el producto no existe, 500 en error interno.
    """
    try:
        # Verificar que existe
        producto_data = tracker.db.obtener_producto(producto_id)
        if not producto_data:
            raise HTTPException(status_code=404, detail="Producto no encontrado")

        # Actualizar
        update_data = producto.model_dump(exclude_unset=True)
        if update_data:
            tracker.db.actualizar_producto(producto_id, **update_data)

        # Retornar actualizado
        return await obtener_producto(producto_id)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al actualizar producto {producto_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{producto_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_producto(producto_id: int):
    """
    Elimina (desactiva) un producto del sistema.

    Args:
        producto_id: ID del producto a eliminar.

    Returns:
        None (HTTP 204 No Content).

    Raises:
        HTTPException: 404 si el producto no existe, 500 en error interno.
    """
    try:
        producto_data = tracker.db.obtener_producto(producto_id)
        if not producto_data:
            raise HTTPException(status_code=404, detail="Producto no encontrado")

        tracker.db.eliminar_producto(producto_id)
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al eliminar producto {producto_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{producto_id}/actualizar-precio", response_model=ActualizarPrecioResponse)
async def actualizar_precio(producto_id: int):
    """
    Actualiza el precio de un producto especifico via scraping.

    Args:
        producto_id: ID del producto a actualizar.

    Returns:
        Resultado de la actualizacion con exito, mensaje y datos del producto.

    Raises:
        HTTPException: 400 si falla la actualizacion, 500 en error interno.
    """
    try:
        resultado = await tracker.actualizar_precio(producto_id)

        if not resultado['exito']:
            raise HTTPException(status_code=400, detail=resultado['mensaje'])

        return ActualizarPrecioResponse(**resultado)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al actualizar precio de producto {producto_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/actualizar-todos", response_model=List[ActualizarPrecioResponse])
async def actualizar_todos_precios():
    """
    Actualiza los precios de todos los productos activos.

    Returns:
        Lista de resultados de actualizacion para cada producto.

    Raises:
        HTTPException: 500 si ocurre un error interno.
    """
    try:
        resultados = await tracker.actualizar_todos_los_precios()
        return [ActualizarPrecioResponse(**r) for r in resultados]
    except Exception as e:
        logger.error(f"Error al actualizar todos los precios: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test-url", response_model=TestURLResponse)
async def test_url(request: TestURLRequest):
    """
    Prueba si una URL es valida y se puede extraer el precio.

    Args:
        request: Objeto con la URL a probar.

    Returns:
        Resultado de la prueba con accesibilidad, precio extraido y dominio.

    Raises:
        HTTPException: 500 si ocurre un error interno.
    """
    try:
        resultado = await tracker.probar_url(request.url)
        return TestURLResponse(**resultado)
    except Exception as e:
        logger.error(f"Error al probar URL {request.url}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/estadisticas/resumen", response_model=EstadisticasResponse)
async def obtener_estadisticas():
    """
    Obtiene estadisticas generales del sistema.

    Returns:
        EstadisticasResponse con total de productos, alertas, registros
        y fecha del ultimo precio actualizado.

    Raises:
        HTTPException: 500 si ocurre un error interno.
    """
    try:
        productos = tracker.db.obtener_productos(solo_activos=True)
        alertas = tracker.db.obtener_alertas()

        total_registros = 0
        ultimo_actualizado = None

        for producto in productos:
            producto_id = producto[0]
            historial = tracker.db.obtener_historial(producto_id)
            total_registros += len(historial)

            if historial:
                fecha_ultimo = historial[-1][0]
                if ultimo_actualizado is None or fecha_ultimo > ultimo_actualizado:
                    ultimo_actualizado = fecha_ultimo

        return EstadisticasResponse(
            total_productos=len(productos),
            total_alertas=len(alertas),
            total_registros=total_registros,
            ultimo_actualizado=ultimo_actualizado
        )
    except Exception as e:
        logger.error(f"Error al obtener estadisticas: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
