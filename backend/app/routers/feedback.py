"""
Router de Feedback
Permite a los usuarios enviar feedback y sugerencias

Author: HellSpawn
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional

from ..database import get_db, Feedback, User
from ..schemas import FeedbackCreate, FeedbackResponse
from ..security import get_current_user
from ..services.email_service import send_feedback_notification

router = APIRouter(prefix="/feedback", tags=["Feedback"])


@router.post("/", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
async def create_feedback(
    feedback_data: FeedbackCreate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    """
    Enviar feedback o sugerencia
    
    - **mensaje**: Mensaje de feedback (10-1000 caracteres)
    - **email**: Email opcional para respuesta
    - **rating**: Calificación opcional (1-5 estrellas)
    
    Nota: Se requiere estar autenticado pero el email es opcional
    """
    # Crear feedback
    new_feedback = Feedback(
        user_id=current_user.id if current_user else None,
        email=feedback_data.email,
        mensaje=feedback_data.mensaje,
        rating=feedback_data.rating
    )
    
    db.add(new_feedback)
    db.commit()
    db.refresh(new_feedback)
    
    # Enviar notificación por email al admin
    notification_data = {
        'username': current_user.username if current_user else None,
        'email': feedback_data.email,
        'mensaje': feedback_data.mensaje,
        'rating': feedback_data.rating
    }
    send_feedback_notification(notification_data)
    
    return new_feedback


@router.post("/anonymous", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
async def create_anonymous_feedback(
    feedback_data: FeedbackCreate,
    db: Session = Depends(get_db)
):
    """
    Enviar feedback anónimo (sin autenticación)
    
    - **mensaje**: Mensaje de feedback (10-1000 caracteres)
    - **email**: Email opcional para respuesta
    - **rating**: Calificación opcional (1-5 estrellas)
    """
    # Crear feedback anónimo
    new_feedback = Feedback(
        user_id=None,
        email=feedback_data.email,
        mensaje=feedback_data.mensaje,
        rating=feedback_data.rating
    )
    
    db.add(new_feedback)
    db.commit()
    db.refresh(new_feedback)
    
    # Enviar notificación por email al admin
    notification_data = {
        'username': None,
        'email': feedback_data.email,
        'mensaje': feedback_data.mensaje,
        'rating': feedback_data.rating
    }
    send_feedback_notification(notification_data)
    
    return new_feedback
