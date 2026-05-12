"""
MCP (Model Context Protocol) Server for Price Tracker
Expone herramientas que Claude puede usar para interactuar con el sistema

Author: Leonardo Temporal
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from .database import get_db, Producto as ProductoModel, HistorialPrecio, User
from .security import get_current_active_user
from .schemas import ProductoCreate
from .utils import detectar_tienda

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.scraper import PriceScraper

router = APIRouter(prefix="/mcp", tags=["MCP Server"])
scraper = PriceScraper()


# ========== Schemas MCP ==========

class MCPToolDefinition(BaseModel):
    name: str
    description: str
    parameters: dict


class MCPToolRequest(BaseModel):
    tool: str
    parameters: dict


class MCPToolResponse(BaseModel):
    success: bool
    result: Optional[dict] = None
    error: Optional[str] = None


class MCPStatusResponse(BaseModel):
    status: str
    version: str
    tools: List[str]


# ========== Definicion de herramientas ==========

TOOLS_DEFINITIONS = [
    {
        "name": "get_product_price",
        "description": "Obtiene el precio actual de un producto por su ID o nombre",
        "parameters": {
            "type": "object",
            "properties": {
                "product_id": {
                    "type": "integer",
                    "description": "ID del producto en el sistema"
                },
                "product_name": {
                    "type": "string",
                    "description": "Nombre del producto (busqueda parcial)"
                }
            },
            "anyOf": [
                {"required": ["product_id"]},
                {"required": ["product_name"]}
            ]
        }
    },
    {
        "name": "add_product",
        "description": "Agrega un nuevo producto para rastrear su precio",
        "parameters": {
            "type": "object",
            "properties": {
                "nombre": {
                    "type": "string",
                    "description": "Nombre descriptivo del producto"
                },
                "url": {
                    "type": "string",
                    "description": "URL del producto en la tienda"
                },
                "precio_objetivo": {
                    "type": "number",
                    "description": "Precio objetivo para recibir alertas (opcional)"
                }
            },
            "required": ["nombre", "url"]
        }
    },
    {
        "name": "get_alerts",
        "description": "Obtiene todas las alertas activas (productos cuyo precio actual es menor o igual al precio objetivo)",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "update_prices",
        "description": "Actualiza los precios de todos los productos realizando scraping",
        "parameters": {
            "type": "object",
            "properties": {
                "product_id": {
                    "type": "integer",
                    "description": "ID especifico del producto a actualizar (opcional, si no se proporciona actualiza todos)"
                }
            }
        }
    },
    {
        "name": "get_products_list",
        "description": "Obtiene la lista de todos los productos rastreados con sus precios actuales",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "get_price_history",
        "description": "Obtiene el historial de precios de un producto especifico",
        "parameters": {
            "type": "object",
            "properties": {
                "product_id": {
                    "type": "integer",
                    "description": "ID del producto"
                }
            },
            "required": ["product_id"]
        }
    }
]


# ========== Endpoints MCP ==========

@router.get("/status", response_model=MCPStatusResponse)
async def mcp_status():
    """
    Estado del servidor MCP y lista de herramientas disponibles
    """
    return MCPStatusResponse(
        status="online",
        version="1.0.0",
        tools=[tool["name"] for tool in TOOLS_DEFINITIONS]
    )


@router.get("/tools", response_model=List[MCPToolDefinition])
async def mcp_list_tools():
    """
    Lista todas las herramientas disponibles con sus definiciones
    """
    return [MCPToolDefinition(**tool) for tool in TOOLS_DEFINITIONS]


@router.post("/tools/call", response_model=MCPToolResponse)
async def mcp_call_tool(
    request: MCPToolRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Ejecuta una herramienta MCP con los parametros proporcionados
    """
    try:
        if request.tool == "get_product_price":
            result = await _get_product_price(request.parameters, current_user, db)
            return MCPToolResponse(success=True, result=result)

        elif request.tool == "add_product":
            result = await _add_product(request.parameters, current_user, db)
            return MCPToolResponse(success=True, result=result)

        elif request.tool == "get_alerts":
            result = await _get_alerts(current_user, db)
            return MCPToolResponse(success=True, result=result)

        elif request.tool == "update_prices":
            result = await _update_prices(request.parameters, current_user, db)
            return MCPToolResponse(success=True, result=result)

        elif request.tool == "get_products_list":
            result = await _get_products_list(current_user, db)
            return MCPToolResponse(success=True, result=result)

        elif request.tool == "get_price_history":
            result = await _get_price_history(request.parameters, current_user, db)
            return MCPToolResponse(success=True, result=result)

        else:
            return MCPToolResponse(
                success=False,
                error=f"Herramienta '{request.tool}' no encontrada"
            )

    except Exception as e:
        return MCPToolResponse(success=False, error=str(e))


# ========== Implementacion de herramientas ==========

async def _get_product_price(params: dict, current_user: User, db: Session) -> dict:
    """Obtiene precio actual de un producto"""
    product_id = params.get("product_id")
    product_name = params.get("product_name")

    query = db.query(ProductoModel).filter(ProductoModel.user_id == current_user.id)

    if product_id:
        producto = query.filter(ProductoModel.id == product_id).first()
    elif product_name:
        producto = query.filter(ProductoModel.nombre.ilike(f"%{product_name}%")).first()
    else:
        raise ValueError("Debe proporcionar product_id o product_name")

    if not producto:
        return {"message": "Producto no encontrado"}

    # Obtener historial
    historial = db.query(HistorialPrecio).filter(
        HistorialPrecio.producto_id == producto.id
    ).order_by(HistorialPrecio.fecha.desc()).all()

    return {
        "id": producto.id,
        "nombre": producto.nombre,
        "url": producto.url,
        "precio_actual": producto.precio_actual,
        "precio_objetivo": producto.precio_objetivo,
        "tienda": producto.tienda,
        "num_registros": len(historial),
        "ultima_actualizacion": historial[0].fecha.isoformat() if historial else None
    }


async def _add_product(params: dict, current_user: User, db: Session) -> dict:
    """Agrega un nuevo producto"""
    nombre = params.get("nombre")
    url = params.get("url")
    precio_objetivo = params.get("precio_objetivo")

    if not nombre or not url:
        raise ValueError("nombre y url son requeridos")

    # Verificar duplicados
    existente = db.query(ProductoModel).filter(
        ProductoModel.user_id == current_user.id,
        ProductoModel.url == url
    ).first()
    if existente:
        return {"message": "Este producto ya fue registrado", "product_id": existente.id}

    # Obtener precio inicial
    precio_inicial = None
    try:
        precio_inicial = await scraper.get_price(url)
    except Exception as e:
        print(f"Error al obtener precio inicial: {e}")

    tienda = detectar_tienda(url)

    nuevo_producto = ProductoModel(
        user_id=current_user.id,
        nombre=nombre,
        url=url,
        precio_objetivo=precio_objetivo,
        precio_actual=precio_inicial,
        tienda=tienda
    )
    db.add(nuevo_producto)
    db.flush()

    if precio_inicial is not None:
        historial = HistorialPrecio(producto_id=nuevo_producto.id, precio=precio_inicial)
        db.add(historial)

    db.commit()
    db.refresh(nuevo_producto)

    return {
        "message": "Producto agregado exitosamente",
        "product_id": nuevo_producto.id,
        "nombre": nuevo_producto.nombre,
        "precio_actual": nuevo_producto.precio_actual,
        "precio_objetivo": nuevo_producto.precio_objetivo
    }


async def _get_alerts(current_user: User, db: Session) -> dict:
    """Obtiene alertas activas"""
    productos = db.query(ProductoModel).filter(
        ProductoModel.user_id == current_user.id,
        ProductoModel.precio_objetivo.isnot(None),
        ProductoModel.precio_actual.isnot(None)
    ).all()

    alertas = []
    for p in productos:
        if p.precio_actual <= p.precio_objetivo:
            ahorro = p.precio_objetivo - p.precio_actual
            porcentaje = (ahorro / p.precio_objetivo) * 100 if p.precio_objetivo else 0
            alertas.append({
                "id": p.id,
                "nombre": p.nombre,
                "precio_actual": p.precio_actual,
                "precio_objetivo": p.precio_objetivo,
                "ahorro": round(ahorro, 2),
                "porcentaje_ahorro": round(porcentaje, 1),
                "url": p.url
            })

    return {"total_alertas": len(alertas), "alertas": alertas}


async def _update_prices(params: dict, current_user: User, db: Session) -> dict:
    """Actualiza precios de productos"""
    product_id = params.get("product_id")

    if product_id:
        productos = db.query(ProductoModel).filter(
            ProductoModel.user_id == current_user.id,
            ProductoModel.id == product_id
        ).all()
    else:
        productos = db.query(ProductoModel).filter(
            ProductoModel.user_id == current_user.id
        ).all()

    resultados = []
    for producto in productos:
        try:
            nuevo_precio = await scraper.get_price(producto.url)
            if nuevo_precio is not None:
                producto.precio_actual = nuevo_precio
                historial = HistorialPrecio(producto_id=producto.id, precio=nuevo_precio)
                db.add(historial)
                resultados.append({
                    "id": producto.id,
                    "nombre": producto.nombre,
                    "precio_actualizado": nuevo_precio,
                    "exito": True
                })
            else:
                resultados.append({
                    "id": producto.id,
                    "nombre": producto.nombre,
                    "exito": False,
                    "error": "No se pudo obtener el precio"
                })
        except Exception as e:
            resultados.append({
                "id": producto.id,
                "nombre": producto.nombre,
                "exito": False,
                "error": str(e)
            })

    db.commit()
    return {"total_actualizados": len(productos), "resultados": resultados}


async def _get_products_list(current_user: User, db: Session) -> dict:
    """Obtiene lista de productos"""
    productos = db.query(ProductoModel).filter(
        ProductoModel.user_id == current_user.id
    ).all()

    items = []
    for p in productos:
        historial_count = db.query(HistorialPrecio).filter(
            HistorialPrecio.producto_id == p.id
        ).count()

        alerta = False
        if p.precio_objetivo and p.precio_actual and p.precio_actual <= p.precio_objetivo:
            alerta = True

        items.append({
            "id": p.id,
            "nombre": p.nombre,
            "url": p.url,
            "precio_actual": p.precio_actual,
            "precio_objetivo": p.precio_objetivo,
            "tienda": p.tienda,
            "num_registros": historial_count,
            "alerta": alerta
        })

    return {"total": len(items), "productos": items}


async def _get_price_history(params: dict, current_user: User, db: Session) -> dict:
    """Obtiene historial de precios"""
    product_id = params.get("product_id")
    if not product_id:
        raise ValueError("product_id es requerido")

    producto = db.query(ProductoModel).filter(
        ProductoModel.id == product_id,
        ProductoModel.user_id == current_user.id
    ).first()

    if not producto:
        return {"message": "Producto no encontrado"}

    historial = db.query(HistorialPrecio).filter(
        HistorialPrecio.producto_id == product_id
    ).order_by(HistorialPrecio.fecha.asc()).all()

    return {
        "producto": {
            "id": producto.id,
            "nombre": producto.nombre,
            "url": producto.url
        },
        "total_registros": len(historial),
        "historial": [
            {"fecha": h.fecha.isoformat(), "precio": h.precio}
            for h in historial
        ]
    }
