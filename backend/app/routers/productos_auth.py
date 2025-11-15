"""
Router de Productos - Endpoints para gestión de productos con autenticación
Requiere token JWT para todas las operaciones

Author: HellSpawn
"""
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from datetime import datetime

from ..database import get_db, Producto as ProductoModel, HistorialPrecio, User
from ..schemas import (
    Producto, ProductoCreate, ProductoUpdate, ProductoDetalle,
    TestURLRequest, TestURLResponse, ActualizarPrecioResponse,
    EstadisticasResponse, PrecioHistorial
)
from ..security import get_current_active_user
from ..utils import detectar_tienda, calcular_ahorro_porcentual

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
from src.scraper import PriceScraper

router = APIRouter(prefix="/productos", tags=["Productos"])
scraper = PriceScraper()


@router.get("/", response_model=List[Producto])
async def listar_productos(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Obtener todos los productos del usuario actual
    Requiere autenticación
    """
    productos = db.query(ProductoModel).filter(
        ProductoModel.user_id == current_user.id
    ).all()
    
    resultado = []
    for p in productos:
        # Obtener estadísticas del historial
        historial = db.query(HistorialPrecio).filter(
            HistorialPrecio.producto_id == p.id
        ).all()
        
        precios = [h.precio for h in historial]
        precio_min = min(precios) if precios else None
        precio_max = max(precios) if precios else None
        
        alerta = False
        if p.precio_objetivo and p.precio_actual and p.precio_actual <= p.precio_objetivo:
            alerta = True
        
        # Calcular ahorro porcentual
        ahorro = calcular_ahorro_porcentual(p.precio_actual, precio_max) if p.precio_actual and precio_max else None
        
        resultado.append(Producto(
            id=p.id,
            nombre=p.nombre,
            url=p.url,
            precio_objetivo=p.precio_objetivo,
            activo=True,
            fecha_creacion=p.created_at.isoformat(),
            precio_actual=p.precio_actual,
            precio_min=precio_min,
            precio_max=precio_max,
            num_registros=len(historial),
            alerta=alerta,
            tienda=p.tienda,
            ahorro_porcentual=ahorro
        ))
    
    return resultado


@router.get("/{producto_id}", response_model=ProductoDetalle)
async def obtener_producto(
    producto_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Obtener detalles de un producto específico con su historial
    Solo puede acceder el dueño del producto
    """
    producto = db.query(ProductoModel).filter(
        ProductoModel.id == producto_id,
        ProductoModel.user_id == current_user.id
    ).first()
    
    if not producto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado"
        )
    
    # Obtener historial ordenado por fecha
    historial = db.query(HistorialPrecio).filter(
        HistorialPrecio.producto_id == producto_id
    ).order_by(HistorialPrecio.fecha.desc()).all()
    
    precios = [h.precio for h in historial]
    precio_min = min(precios) if precios else None
    precio_max = max(precios) if precios else None
    
    alerta = False
    if producto.precio_objetivo and producto.precio_actual and producto.precio_actual <= producto.precio_objetivo:
        alerta = True
    
    return ProductoDetalle(
        id=producto.id,
        nombre=producto.nombre,
        url=producto.url,
        precio_objetivo=producto.precio_objetivo,
        activo=True,
        fecha_creacion=producto.created_at.isoformat(),
        precio_actual=producto.precio_actual,
        precio_min=precio_min,
        precio_max=precio_max,
        num_registros=len(historial),
        alerta=alerta,
        historial=[
            PrecioHistorial(fecha=h.fecha.isoformat(), precio=h.precio)
            for h in historial
        ]
    )


@router.post("/", response_model=Producto, status_code=status.HTTP_201_CREATED)
async def crear_producto(
    producto: ProductoCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Crear un nuevo producto y obtener su precio inicial
    Se asocia automáticamente al usuario actual
    """
    try:
        # Obtener precio inicial
        precio_inicial = scraper.get_price(producto.url)
        
        # Crear producto
        nuevo_producto = ProductoModel(
            user_id=current_user.id,
            nombre=producto.nombre,
            url=producto.url,
            precio_objetivo=producto.precio_objetivo,
            precio_actual=precio_inicial,
            tienda=detectar_tienda(producto.url)
        )
        
        db.add(nuevo_producto)
        db.commit()
        db.refresh(nuevo_producto)
        
        # Agregar precio al historial
        if precio_inicial:
            historial = HistorialPrecio(
                producto_id=nuevo_producto.id,
                precio=precio_inicial
            )
            db.add(historial)
            db.commit()
        
        alerta = False
        if producto.precio_objetivo and precio_inicial and precio_inicial <= producto.precio_objetivo:
            alerta = True
        
        return Producto(
            id=nuevo_producto.id,
            nombre=nuevo_producto.nombre,
            url=nuevo_producto.url,
            precio_objetivo=nuevo_producto.precio_objetivo,
            activo=True,
            fecha_creacion=nuevo_producto.created_at.isoformat(),
            precio_actual=precio_inicial,
            precio_min=precio_inicial,
            precio_max=precio_inicial,
            num_registros=1 if precio_inicial else 0,
            alerta=alerta,
            tienda=nuevo_producto.tienda,
            ahorro_porcentual=None
        )
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear producto: {str(e)}"
        )


@router.put("/{producto_id}", response_model=Producto)
async def actualizar_producto(
    producto_id: int,
    producto_update: ProductoUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Actualizar información de un producto
    Solo puede actualizar el dueño del producto
    """
    producto = db.query(ProductoModel).filter(
        ProductoModel.id == producto_id,
        ProductoModel.user_id == current_user.id
    ).first()
    
    if not producto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado"
        )
    
    # Actualizar campos
    if producto_update.nombre is not None:
        producto.nombre = producto_update.nombre
    if producto_update.precio_objetivo is not None:
        producto.precio_objetivo = producto_update.precio_objetivo
    
    db.commit()
    db.refresh(producto)
    
    # Obtener estadísticas
    historial = db.query(HistorialPrecio).filter(
        HistorialPrecio.producto_id == producto_id
    ).all()
    
    precios = [h.precio for h in historial]
    precio_min = min(precios) if precios else None
    precio_max = max(precios) if precios else None
    
    alerta = False
    if producto.precio_objetivo and producto.precio_actual and producto.precio_actual <= producto.precio_objetivo:
        alerta = True
    
    return Producto(
        id=producto.id,
        nombre=producto.nombre,
        url=producto.url,
        precio_objetivo=producto.precio_objetivo,
        activo=True,
        fecha_creacion=producto.created_at.isoformat(),
        precio_actual=producto.precio_actual,
        precio_min=precio_min,
        precio_max=precio_max,
        num_registros=len(historial),
        alerta=alerta
    )


@router.delete("/{producto_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_producto(
    producto_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Eliminar un producto y todo su historial
    Solo puede eliminar el dueño del producto
    """
    producto = db.query(ProductoModel).filter(
        ProductoModel.id == producto_id,
        ProductoModel.user_id == current_user.id
    ).first()
    
    if not producto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado"
        )
    
    db.delete(producto)
    db.commit()
    
    return None


@router.post("/{producto_id}/actualizar-precio", response_model=ActualizarPrecioResponse)
async def actualizar_precio(
    producto_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Actualizar el precio de un producto específico
    Realiza scraping y guarda en historial
    """
    producto = db.query(ProductoModel).filter(
        ProductoModel.id == producto_id,
        ProductoModel.user_id == current_user.id
    ).first()
    
    if not producto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado"
        )
    
    try:
        # Obtener nuevo precio
        nuevo_precio = scraper.get_price(producto.url)
        
        if nuevo_precio is None:
            return ActualizarPrecioResponse(
                exito=False,
                mensaje="No se pudo obtener el precio",
                producto_id=producto_id,
                nombre=producto.nombre,
                alerta=False
            )
        
        # Actualizar precio actual
        producto.precio_actual = nuevo_precio
        db.commit()
        
        # Agregar al historial
        historial = HistorialPrecio(
            producto_id=producto_id,
            precio=nuevo_precio
        )
        db.add(historial)
        db.commit()
        
        alerta = False
        if producto.precio_objetivo and nuevo_precio <= producto.precio_objetivo:
            alerta = True
        
        return ActualizarPrecioResponse(
            exito=True,
            mensaje="Precio actualizado correctamente",
            producto_id=producto_id,
            nombre=producto.nombre,
            precio_actual=nuevo_precio,
            precio_objetivo=producto.precio_objetivo,
            alerta=alerta
        )
    
    except Exception as e:
        return ActualizarPrecioResponse(
            exito=False,
            mensaje=f"Error: {str(e)}",
            producto_id=producto_id,
            nombre=producto.nombre,
            alerta=False
        )


@router.post("/actualizar-todos", response_model=List[ActualizarPrecioResponse])
async def actualizar_todos_precios(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Actualizar precios de todos los productos del usuario
    Puede tardar varios segundos dependiendo de la cantidad
    """
    productos = db.query(ProductoModel).filter(
        ProductoModel.user_id == current_user.id
    ).all()
    
    resultados = []
    
    for producto in productos:
        try:
            nuevo_precio = scraper.get_price(producto.url)
            
            if nuevo_precio is None:
                resultados.append(ActualizarPrecioResponse(
                    exito=False,
                    mensaje="No se pudo obtener el precio",
                    producto_id=producto.id,
                    nombre=producto.nombre,
                    alerta=False
                ))
                continue
            
            producto.precio_actual = nuevo_precio
            
            historial = HistorialPrecio(
                producto_id=producto.id,
                precio=nuevo_precio
            )
            db.add(historial)
            
            alerta = False
            if producto.precio_objetivo and nuevo_precio <= producto.precio_objetivo:
                alerta = True
            
            resultados.append(ActualizarPrecioResponse(
                exito=True,
                mensaje="Actualizado",
                producto_id=producto.id,
                nombre=producto.nombre,
                precio_actual=nuevo_precio,
                precio_objetivo=producto.precio_objetivo,
                alerta=alerta
            ))
        
        except Exception as e:
            resultados.append(ActualizarPrecioResponse(
                exito=False,
                mensaje=f"Error: {str(e)}",
                producto_id=producto.id,
                nombre=producto.nombre,
                alerta=False
            ))
    
    db.commit()
    return resultados


@router.post("/test-url", response_model=TestURLResponse)
async def test_url(
    request: TestURLRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Probar si una URL es accesible y se puede extraer el precio
    No requiere crear el producto
    """
    try:
        precio = scraper.get_price(request.url)
        
        from urllib.parse import urlparse
        domain = urlparse(request.url).netloc
        
        return TestURLResponse(
            url=request.url,
            accesible=precio is not None,
            precio=precio,
            error=None if precio else "No se pudo extraer el precio",
            domain=domain
        )
    
    except Exception as e:
        return TestURLResponse(
            url=request.url,
            accesible=False,
            precio=None,
            error=str(e),
            domain=""
        )


@router.get("/estadisticas/resumen", response_model=EstadisticasResponse)
async def obtener_estadisticas(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Obtener estadísticas generales del usuario
    Total de productos, alertas activas, registros totales
    """
    # Total de productos
    total_productos = db.query(func.count(ProductoModel.id)).filter(
        ProductoModel.user_id == current_user.id
    ).scalar()
    
    # Total de alertas (productos con precio <= precio_objetivo)
    productos_con_alertas = db.query(ProductoModel).filter(
        ProductoModel.user_id == current_user.id,
        ProductoModel.precio_objetivo.isnot(None),
        ProductoModel.precio_actual.isnot(None)
    ).all()
    
    total_alertas = sum(
        1 for p in productos_con_alertas
        if p.precio_actual <= p.precio_objetivo
    )
    
    # Total de registros en historial
    producto_ids = [p.id for p in db.query(ProductoModel.id).filter(
        ProductoModel.user_id == current_user.id
    ).all()]
    
    total_registros = db.query(func.count(HistorialPrecio.id)).filter(
        HistorialPrecio.producto_id.in_(producto_ids)
    ).scalar() if producto_ids else 0
    
    # Última actualización
    ultimo_registro = db.query(HistorialPrecio).filter(
        HistorialPrecio.producto_id.in_(producto_ids)
    ).order_by(HistorialPrecio.fecha.desc()).first() if producto_ids else None
    
    return EstadisticasResponse(
        total_productos=total_productos or 0,
        total_alertas=total_alertas,
        total_registros=total_registros or 0,
        ultimo_actualizado=ultimo_registro.fecha.isoformat() if ultimo_registro else None
    )
