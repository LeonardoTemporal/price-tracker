"""
Security utilities for authentication
Handles password hashing, JWT tokens, and user verification

Author: HellSpawn
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv

from .database import get_db, User

load_dotenv()

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verificar contraseña contra hash"""
    try:
        # Si el hash ya es bytes, usarlo directamente
        if isinstance(hashed_password, bytes):
            hash_bytes = hashed_password
        else:
            # Si es string, convertir a bytes
            hash_bytes = hashed_password.encode('utf-8')
        
        return bcrypt.checkpw(plain_password.encode('utf-8'), hash_bytes)
    except Exception as e:
        print(f"Error en verify_password: {e}")
        return False


def get_password_hash(password: str) -> str:
    """Generar hash de contraseña"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Crear token JWT"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> dict:
    """Decodificar y validar token JWT"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(f"Token decodificado exitosamente: {payload}")
        return payload
    except JWTError as e:
        print(f"ERROR al decodificar token: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        print(f"ERROR inesperado al decodificar token: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Obtener usuario actual desde el token"""
    print(f"Token recibido: {token[:20]}..." if len(token) > 20 else f"Token recibido: {token}")
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = decode_token(token)
        user_id_str: str = payload.get("sub")
        print(f"User ID del token: {user_id_str}, tipo: {type(user_id_str)}")
        
        if user_id_str is None:
            print("ERROR: user_id es None")
            raise credentials_exception
        
        # Convertir string a int
        user_id = int(user_id_str)
        
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            print(f"ERROR: Usuario con id {user_id} no encontrado en BD")
            raise credentials_exception
        
        if not user.is_active:
            print(f"ERROR: Usuario {user.username} está inactivo")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuario inactivo"
            )
        
        print(f"Usuario autenticado: {user.username}")
        return user
    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR en get_current_user: {e}")
        raise credentials_exception


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Obtener usuario activo actual"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Usuario inactivo")
    return current_user
