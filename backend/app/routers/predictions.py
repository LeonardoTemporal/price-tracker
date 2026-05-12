"""
AI Price Prediction Router
Prediccion de precios usando regresion lineal con scikit-learn

Author: Leonardo Temporal
"""
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import numpy as np

from ..database import get_db, Producto as ProductoModel, HistorialPrecio, User
from ..security import get_current_active_user

router = APIRouter(prefix="/predict", tags=["AI Prediction"])


# ========== Schemas ==========

class PricePredictionResponse(BaseModel):
    product_id: int
    nombre: str
    precio_actual: Optional[float]
    prediccion_siguiente: Optional[float]
    tendencia: str  # "subiendo", "bajando", "estable"
    confianza: float  # 0-1
    dias_estimados_objetivo: Optional[int] = None
    mensaje: str
    datos_suficientes: bool
    historial_usado: int


class PriceTrendItem(BaseModel):
    fecha: str
    precio: float


class PriceTrendResponse(BaseModel):
    product_id: int
    nombre: str
    tendencia: str
    porcentaje_cambio: Optional[float]
    precio_promedio: float
    precio_minimo: float
    precio_maximo: float
    historial: List[PriceTrendItem]


# ========== Helper Functions ==========

def calcular_prediccion(historial_precios: list) -> dict:
    """
    Calcula prediccion de precio usando regresion lineal simple
    """
    if len(historial_precios) < 3:
        return {
            "datos_suficientes": False,
            "prediccion": None,
            "confianza": 0.0,
            "tendencia": "estable",
            "mensaje": "Se necesitan al menos 3 registros de precio para hacer una prediccion"
        }

    # Preparar datos: X = indice temporal, y = precio
    X = np.array([[i] for i in range(len(historial_precios))])
    y = np.array([h.precio for h in historial_precios])

    # Calcular regresion lineal manualmente (sin sklearn para evitar dependencia pesada)
    # y = mx + b
    n = len(X)
    sum_x = np.sum(X)
    sum_y = np.sum(y)
    sum_xy = np.sum(X.flatten() * y)
    sum_x2 = np.sum(X ** 2)

    # Pendiente (m) e intercepto (b)
    denominator = (n * sum_x2 - sum_x ** 2)
    if denominator == 0:
        return {
            "datos_suficientes": False,
            "prediccion": None,
            "confianza": 0.0,
            "tendencia": "estable",
            "mensaje": "No se puede calcular la tendencia con los datos actuales"
        }

    m = (n * sum_xy - sum_x * sum_y) / denominator
    b = (sum_y - m * sum_x) / n

    # Prediccion para el siguiente punto
    siguiente_x = len(historial_precios)
    prediccion = m * siguiente_x + b

    # Calcular R-cuadrado (coeficiente de determinacion) como medida de confianza
    y_mean = np.mean(y)
    ss_tot = np.sum((y - y_mean) ** 2)
    y_pred = m * X.flatten() + b
    ss_res = np.sum((y - y_pred) ** 2)
    r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0

    # Determinar tendencia
    if m > 0.5:
        tendencia = "subiendo"
    elif m < -0.5:
        tendencia = "bajando"
    else:
        tendencia = "estable"

    # Calcular dias estimados para llegar al precio objetivo
    dias_estimados = None
    if m < 0 and len(historial_precios) >= 3:
        # Precio bajando: estimar cuando llega a cierto valor
        pass  # Se calcula en el endpoint con el precio objetivo

    return {
        "datos_suficientes": True,
        "prediccion": round(float(prediccion), 2),
        "confianza": round(float(max(0, r_squared)), 2),
        "tendencia": tendencia,
        "pendiente": round(float(m), 4),
        "mensaje": "Prediccion calculada exitosamente"
    }


# ========== Endpoints ==========

@router.get("/{producto_id}", response_model=PricePredictionResponse)
async def predict_price(
    producto_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Predice el proximo precio de un producto usando regresion lineal
    sobre su historial de precios
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
    ).order_by(HistorialPrecio.fecha.asc()).all()

    if len(historial) < 3:
        return PricePredictionResponse(
            product_id=producto_id,
            nombre=producto.nombre,
            precio_actual=producto.precio_actual,
            prediccion_siguiente=None,
            tendencia="estable",
            confianza=0.0,
            mensaje="Se necesitan al menos 3 registros de precio para hacer una prediccion",
            datos_suficientes=False,
            historial_usado=len(historial)
        )

    # Calcular prediccion
    resultado = calcular_prediccion(historial)

    # Calcular dias estimados para precio objetivo
    dias_estimados = None
    if (resultado["datos_suficientes"] and
        resultado["tendencia"] == "bajando" and
        producto.precio_objetivo and
        resultado["prediccion"] and
        resultado["prediccion"] > producto.precio_objetivo):

        # Si la tendencia es bajista y la prediccion aun no alcanza el objetivo
        # Estimar cuantos registros mas se necesitan
        pendiente = resultado.get("pendiente", 0)
        if pendiente < 0:
            precio_diferencia = resultado["prediccion"] - producto.precio_objetivo
            if precio_diferencia > 0:
                # Asumiendo un registro cada ~3 dias
                registros_necesarios = abs(precio_diferencia / pendiente)
                dias_estimados = int(registros_necesarios * 3)

    elif (resultado["datos_suficientes"] and
          resultado["tendencia"] == "bajando" and
          producto.precio_objetivo and
          resultado["prediccion"] and
          resultado["prediccion"] <= producto.precio_objetivo):
        dias_estimados = 0  # Ya deberia estar al precio objetivo

    return PricePredictionResponse(
        product_id=producto_id,
        nombre=producto.nombre,
        precio_actual=producto.precio_actual,
        prediccion_siguiente=resultado.get("prediccion"),
        tendencia=resultado["tendencia"],
        confianza=resultado["confianza"],
        dias_estimados_objetivo=dias_estimados,
        mensaje=resultado["mensaje"],
        datos_suficientes=resultado["datos_suficientes"],
        historial_usado=len(historial)
    )


@router.get("/{producto_id}/trend", response_model=PriceTrendResponse)
async def get_price_trend(
    producto_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene la tendencia de precios de un producto con analisis estadistico
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

    historial = db.query(HistorialPrecio).filter(
        HistorialPrecio.producto_id == producto_id
    ).order_by(HistorialPrecio.fecha.asc()).all()

    if not historial:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No hay historial de precios para este producto"
        )

    precios = [h.precio for h in historial]
    precio_min = min(precios)
    precio_max = max(precios)
    precio_promedio = sum(precios) / len(precios)

    # Calcular cambio porcentual total
    if len(historial) >= 2:
        cambio = ((precios[-1] - precios[0]) / precios[0]) * 100
    else:
        cambio = 0

    # Determinar tendencia
    if len(historial) >= 3:
        resultado = calcular_prediccion(historial)
        tendencia = resultado["tendencia"]
    else:
        tendencia = "estable"

    return PriceTrendResponse(
        product_id=producto_id,
        nombre=producto.nombre,
        tendencia=tendencia,
        porcentaje_cambio=round(cambio, 2),
        precio_promedio=round(precio_promedio, 2),
        precio_minimo=round(precio_min, 2),
        precio_maximo=round(precio_max, 2),
        historial=[
            PriceTrendItem(fecha=h.fecha.isoformat(), precio=h.precio)
            for h in historial
        ]
    )
