"""Router de Alertas autenticado."""
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db, Producto as ProductoModel, User
from ..schemas import Alerta
from ..security import get_current_active_user

router = APIRouter(prefix="/alertas", tags=["Alertas"])


@router.get("/", response_model=List[Alerta])
async def obtener_alertas(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obtiene alertas activas del usuario."""
    productos = db.query(ProductoModel).filter(
        ProductoModel.user_id == current_user.id,
        ProductoModel.precio_objetivo.isnot(None),
        ProductoModel.precio_actual.isnot(None)
    ).all()
    
    alertas = []
    for producto in productos:
        if producto.precio_actual <= producto.precio_objetivo:
            ahorro = producto.precio_objetivo - producto.precio_actual
            porcentaje = (ahorro / producto.precio_objetivo) * 100 if producto.precio_objetivo else 0
            alertas.append(Alerta(
                id=producto.id,
                nombre=producto.nombre,
                precio_actual=producto.precio_actual,
                precio_objetivo=producto.precio_objetivo,
                ahorro=round(ahorro, 2),
                porcentaje_ahorro=round(porcentaje, 1)
            ))
    
    return alertas
