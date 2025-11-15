"""
Router de autenticación
Maneja registro, login, verificación de email y gestión de usuarios

Author: HellSpawn
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta, datetime

from ..database import get_db, User, EmailVerification
from ..schemas import (
    UserCreate, User as UserSchema, Token, UserLogin,
    SendVerificationRequest, VerifyEmailRequest, VerifyEmailResponse,
    UserUpdate, PasswordUpdate, ThemePreference
)
from ..security import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_current_active_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from ..services.email_service import (
    generate_verification_code,
    send_verification_email,
    send_welcome_email
)

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.get("/check-username/{username}")
async def check_username_availability(username: str, db: Session = Depends(get_db)):
    """
    Verificar si un nombre de usuario está disponible
    
    - **username**: Nombre de usuario a verificar
    
    Returns:
    - **available**: True si está disponible, False si ya está en uso
    """
    try:
        existing_user = db.query(User).filter(User.username == username).first()
        return {
            "username": username,
            "available": existing_user is None
        }
    except Exception as e:
        print(f"Error checking username: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al verificar disponibilidad: {str(e)}"
        )


@router.post("/register", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Registrar nuevo usuario
    
    - **email**: Email único del usuario
    - **username**: Nombre de usuario único (3-50 caracteres)
    - **password**: Contraseña (mínimo 6 caracteres)
    """
    # Verificar si el email ya existe
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El email ya está registrado"
        )
    
    # Verificar si el username ya existe
    existing_username = db.query(User).filter(User.username == user_data.username).first()
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El nombre de usuario ya está en uso"
        )
    
    # Crear nuevo usuario
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Iniciar sesión y obtener token JWT
    
    - **username**: Nombre de usuario o email
    - **password**: Contraseña
    """
    # Limpiar espacios en blanco del username
    username = form_data.username.strip()
    
    print(f"Intento de login con username: {username}")
    
    # Buscar usuario por username o email
    user = db.query(User).filter(
        (User.username == username) | (User.email == username)
    ).first()
    
    if not user:
        print(f"Usuario no encontrado: {username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    print(f"Usuario encontrado: {user.username}, verificando contraseña...")
    password_valid = verify_password(form_data.password, user.hashed_password)
    print(f"Contraseña válida: {password_valid}")
    
    if not password_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo"
        )
    
    # Crear token de acceso
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)},  # Convertir user.id a string
        expires_delta=access_token_expires
    )
    
    print(f"Login exitoso para {user.username}, token generado")
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }


@router.post("/login/json", response_model=Token)
async def login_json(user_data: UserLogin, db: Session = Depends(get_db)):
    """
    Iniciar sesión con JSON (alternativa a form-data)
    
    - **username**: Nombre de usuario o email
    - **password**: Contraseña
    """
    # Buscar usuario por username o email
    user = db.query(User).filter(
        (User.username == user_data.username) | (User.email == user_data.username)
    ).first()
    
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo"
        )
    
    # Crear token de acceso
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.id},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }


@router.get("/me", response_model=UserSchema)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """
    Obtener información del usuario actual
    Requiere token JWT válido
    """
    return current_user


@router.put("/me/deactivate")
async def deactivate_account(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Desactivar cuenta de usuario
    """
    current_user.is_active = False
    db.commit()
    
    return {"message": "Cuenta desactivada exitosamente"}


@router.post("/send-verification")
async def send_verification(
    request: SendVerificationRequest,
    db: Session = Depends(get_db)
):
    """
    Enviar código de verificación al email del usuario
    
    - **email**: Email del usuario registrado
    """
    # Buscar usuario por email
    user = db.query(User).filter(User.email == request.email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    if user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El email ya ha sido verificado"
        )
    
    # Generar código de verificación
    code = generate_verification_code()
    expires_at = datetime.utcnow() + timedelta(minutes=15)
    
    # Guardar código en la base de datos
    verification = EmailVerification(
        user_id=user.id,
        code=code,
        expires_at=expires_at
    )
    
    db.add(verification)
    db.commit()
    
    # Enviar email
    email_sent = send_verification_email(user.email, user.username, code)
    
    if not email_sent:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al enviar el email de verificación"
        )
    
    return {
        "message": "Código de verificación enviado",
        "email": user.email,
        "expires_in_minutes": 15
    }


@router.post("/verify-email", response_model=VerifyEmailResponse)
async def verify_email(
    request: VerifyEmailRequest,
    db: Session = Depends(get_db)
):
    """
    Verificar email con código de 6 dígitos
    
    - **email**: Email del usuario
    - **code**: Código de verificación de 6 dígitos
    """
    # Buscar usuario
    user = db.query(User).filter(User.email == request.email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    if user.email_verified:
        return VerifyEmailResponse(
            message="El email ya ha sido verificado",
            email_verified=True
        )
    
    # Buscar código de verificación válido
    verification = db.query(EmailVerification).filter(
        EmailVerification.user_id == user.id,
        EmailVerification.code == request.code,
        EmailVerification.is_used == False,
        EmailVerification.expires_at > datetime.utcnow()
    ).first()
    
    if not verification:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Código inválido o expirado"
        )
    
    # Marcar código como usado
    verification.is_used = True
    
    # Marcar email como verificado
    user.email_verified = True
    
    db.commit()
    
    # Enviar email de bienvenida
    send_welcome_email(user.email, user.username)
    
    return VerifyEmailResponse(
        message="Email verificado exitosamente",
        email_verified=True
    )


@router.put("/me/profile", response_model=UserSchema)
async def update_profile(
    profile_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Actualizar perfil del usuario (username o email)
    
    - **username**: Nuevo nombre de usuario (opcional)
    - **email**: Nuevo email (opcional)
    """
    # Verificar si el nuevo username ya existe
    if profile_update.username and profile_update.username != current_user.username:
        existing = db.query(User).filter(User.username == profile_update.username).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El nombre de usuario ya está en uso"
            )
        current_user.username = profile_update.username
    
    # Verificar si el nuevo email ya existe
    if profile_update.email and profile_update.email != current_user.email:
        existing = db.query(User).filter(User.email == profile_update.email).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El email ya está registrado"
            )
        current_user.email = profile_update.email
        current_user.email_verified = False  # Requiere re-verificación
    
    current_user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(current_user)
    
    return current_user


@router.put("/me/password")
async def update_password(
    password_update: PasswordUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Cambiar contraseña del usuario
    
    - **current_password**: Contraseña actual
    - **new_password**: Nueva contraseña (mínimo 6 caracteres)
    """
    # Verificar contraseña actual
    if not verify_password(password_update.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contraseña actual incorrecta"
        )
    
    # Actualizar contraseña
    current_user.hashed_password = get_password_hash(password_update.new_password)
    current_user.updated_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Contraseña actualizada exitosamente"}


@router.put("/me/theme", response_model=UserSchema)
async def update_theme(
    theme: ThemePreference,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Actualizar preferencia de tema (modo oscuro/claro)
    
    - **dark_mode**: true para modo oscuro, false para modo claro
    """
    current_user.dark_mode = theme.dark_mode
    current_user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(current_user)
    
    return current_user


@router.delete("/me/account")
async def delete_account(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Eliminar cuenta de usuario (soft delete)
    
    La cuenta se desactiva pero los datos se mantienen.
    El usuario no podrá iniciar sesión pero sus productos se conservan.
    """
    current_user.is_active = False
    current_user.updated_at = datetime.utcnow()
    db.commit()
    
    return {
        "message": "Cuenta desactivada exitosamente",
        "note": "Tus datos se han conservado. Contacta al soporte para reactivar tu cuenta."
    }


@router.get("/admin/clear-all-users")
async def clear_all_users(
    admin_secret: str,
    db: Session = Depends(get_db)
):
    """
    ADMIN: Eliminar todos los usuarios de la base de datos
    Requiere admin_secret para autorización
    """
    # Verificar secret
    if admin_secret != "HellSpawn2025":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No autorizado"
        )
    
    try:
        from sqlalchemy import text
        
        # Contar usuarios actuales
        count = db.query(User).count()
        
        # Eliminar manualmente en orden para evitar problemas de FK
        db.execute(text("DELETE FROM feedback"))
        db.execute(text("DELETE FROM email_verifications"))
        db.execute(text("DELETE FROM historial_precios"))
        db.execute(text("DELETE FROM productos"))
        db.execute(text("DELETE FROM users"))
        db.commit()
        
        return {
            "message": "Todos los usuarios eliminados",
            "usuarios_eliminados": count
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar usuarios: {str(e)}"
        )
