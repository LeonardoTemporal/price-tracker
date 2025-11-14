"""
Router de Historial - Endpoints para consultar historial de precios
"""
from fastapi import APIRouter, HTTPException
from typing import List
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from src.tracker import Tracker
from backend.app.schemas import PrecioHistorial

router = APIRouter()
tracker = Tracker()


@router.get("/{producto_id}", response_model=List[PrecioHistorial])
async def obtener_historial(producto_id: int):
    """Obtiene el historial completo de precios de un producto."""
    try:
        # Verificar que el producto existe
        producto = tracker.db.obtener_producto(producto_id)
        if not producto:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        
        historial_raw = tracker.db.obtener_historial(producto_id)
        historial = [PrecioHistorial(fecha=fecha, precio=precio) for fecha, precio in historial_raw]
        
        return historial
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
