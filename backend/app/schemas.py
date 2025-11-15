"""
Modelos Pydantic para validación de datos

Author: HellSpawn
"""
from pydantic import BaseModel, HttpUrl, Field, EmailStr
from typing import Optional, List
from datetime import datetime


# ========== Schemas de Autenticación ==========

class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=100)


class UserLogin(BaseModel):
    username: str
    password: str


class User(UserBase):
    id: int
    is_active: bool
    email_verified: bool
    dark_mode: bool = False
    created_at: datetime

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None


class PasswordUpdate(BaseModel):
    current_password: str = Field(..., min_length=6)
    new_password: str = Field(..., min_length=6, max_length=100)


class ThemePreference(BaseModel):
    dark_mode: bool


class Token(BaseModel):
    access_token: str
    token_type: str
    user: User


class TokenData(BaseModel):
    user_id: Optional[int] = None


# ========== Schemas de Productos ==========

class ProductoBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=200, description="Nombre del producto")
    url: str = Field(..., description="URL del producto")
    precio_objetivo: Optional[float] = Field(None, ge=0, description="Precio objetivo para alertas")


class ProductoCreate(ProductoBase):
    pass


class ProductoUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=1, max_length=200)
    precio_objetivo: Optional[float] = Field(None, ge=0)
    activo: Optional[bool] = None


class Producto(ProductoBase):
    id: int
    activo: bool
    fecha_creacion: str
    precio_actual: Optional[float] = None
    precio_min: Optional[float] = None
    precio_max: Optional[float] = None
    num_registros: int = 0
    alerta: bool = False
    tienda: Optional[str] = None
    ahorro_porcentual: Optional[float] = None

    class Config:
        from_attributes = True


class PrecioHistorial(BaseModel):
    fecha: str
    precio: float


class ProductoDetalle(Producto):
    historial: List[PrecioHistorial] = []


class Alerta(BaseModel):
    id: int
    nombre: str
    precio_actual: float
    precio_objetivo: float
    ahorro: float
    porcentaje_ahorro: float


class TestURLRequest(BaseModel):
    url: str


class TestURLResponse(BaseModel):
    url: str
    accesible: bool
    precio: Optional[float]
    error: Optional[str]
    domain: str


class ActualizarPrecioResponse(BaseModel):
    exito: bool
    mensaje: str
    producto_id: int
    nombre: Optional[str] = None
    precio_actual: Optional[float] = None
    precio_objetivo: Optional[float] = None
    alerta: bool = False


class EstadisticasResponse(BaseModel):
    total_productos: int
    total_alertas: int
    total_registros: int
    ultimo_actualizado: Optional[str] = None


# ========== Schemas de Verificación de Email ==========

class SendVerificationRequest(BaseModel):
    email: EmailStr


class VerifyEmailRequest(BaseModel):
    email: EmailStr
    code: str = Field(..., min_length=6, max_length=6)


class VerifyEmailResponse(BaseModel):
    message: str
    email_verified: bool


# ========== Schemas de Feedback ==========

class FeedbackCreate(BaseModel):
    mensaje: str = Field(..., min_length=10, max_length=1000)
    email: Optional[EmailStr] = None
    rating: Optional[int] = Field(None, ge=1, le=5)


class FeedbackResponse(BaseModel):
    id: int
    mensaje: str
    email: Optional[str]
    rating: Optional[int]
    created_at: datetime
    
    class Config:
        from_attributes = True
