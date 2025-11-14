"""
Router de Alertas - Endpoints para gestión de alertas de precios
"""
from fastapi import APIRouter, HTTPException
from typing import List
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from src.tracker import Tracker
from backend.app.schemas import Alerta

router = APIRouter()
tracker = Tracker()


@router.get("/", response_model=List[Alerta])
async def obtener_alertas():
    """Obtiene todas las alertas activas (productos que alcanzaron el precio objetivo)."""
    try:
        alertas_data = tracker.obtener_alertas()
        alertas = [Alerta(**alerta) for alerta in alertas_data]
        return alertas
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
