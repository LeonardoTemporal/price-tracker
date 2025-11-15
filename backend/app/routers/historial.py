"""Router de historial autenticado."""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db, Producto as ProductoModel, HistorialPrecio, User
from ..schemas import PrecioHistorial
from ..security import get_current_active_user

router = APIRouter(prefix="/historial", tags=["Historial"])


@router.get("/{producto_id}", response_model=List[PrecioHistorial])
async def obtener_historial(
    producto_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obtiene el historial completo de precios de un producto del usuario."""
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
    
    return [
        PrecioHistorial(
            fecha=registro.fecha.isoformat(),
            precio=registro.precio
        )
        for registro in historial
    ]
