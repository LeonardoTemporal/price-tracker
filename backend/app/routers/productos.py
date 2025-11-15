"""
Router de Productos - Endpoints para gestión de productos
"""
from fastapi import APIRouter, HTTPException, status
from typing import List
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from src.tracker import Tracker
from backend.app.schemas import (
    Producto, ProductoCreate, ProductoUpdate, ProductoDetalle,
    TestURLRequest, TestURLResponse, ActualizarPrecioResponse,
    EstadisticasResponse
)

router = APIRouter()
tracker = Tracker()


@router.get("/", response_model=List[Producto])
async def listar_productos(activos_solo: bool = True):
    """Obtiene la lista de todos los productos."""
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
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{producto_id}", response_model=ProductoDetalle)
async def obtener_producto(producto_id: int):
    """Obtiene los detalles de un producto específico con su historial."""
    try:
        producto_data = tracker.db.obtener_producto(producto_id)
        
        if not producto_data:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        
        id, nombre, url, precio_objetivo, activo, fecha_creacion = producto_data
        
        # Obtener historial
        historial_raw = tracker.db.obtener_historial(producto_id)
        historial = [{"fecha": fecha, "precio": precio} for fecha, precio in historial_raw]
        
        # Estadísticas
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
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", response_model=Producto, status_code=status.HTTP_201_CREATED)
async def crear_producto(producto: ProductoCreate):
    """Crea un nuevo producto y obtiene su precio inicial."""
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
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{producto_id}", response_model=Producto)
async def actualizar_producto(producto_id: int, producto: ProductoUpdate):
    """Actualiza la información de un producto."""
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
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{producto_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_producto(producto_id: int):
    """Elimina (desactiva) un producto."""
    try:
        producto_data = tracker.db.obtener_producto(producto_id)
        if not producto_data:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        
        tracker.db.eliminar_producto(producto_id)
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{producto_id}/actualizar-precio", response_model=ActualizarPrecioResponse)
async def actualizar_precio(producto_id: int):
    """Actualiza el precio de un producto específico."""
    try:
        resultado = await tracker.actualizar_precio(producto_id)
        
        if not resultado['exito']:
            raise HTTPException(status_code=400, detail=resultado['mensaje'])
        
        return ActualizarPrecioResponse(**resultado)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/actualizar-todos", response_model=List[ActualizarPrecioResponse])
async def actualizar_todos_precios():
    """Actualiza los precios de todos los productos activos."""
    try:
        resultados = await tracker.actualizar_todos_los_precios()
        return [ActualizarPrecioResponse(**r) for r in resultados]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test-url", response_model=TestURLResponse)
async def test_url(request: TestURLRequest):
    """Prueba si una URL es válida y se puede extraer el precio."""
    try:
        resultado = tracker.probar_url(request.url)
        return TestURLResponse(**resultado)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/estadisticas/resumen", response_model=EstadisticasResponse)
async def obtener_estadisticas():
    """Obtiene estadísticas generales del sistema."""
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
        raise HTTPException(status_code=500, detail=str(e))
