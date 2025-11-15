"""
Database configuration and models for Price Tracker
Uses SQLAlchemy ORM with PostgreSQL

Author: HellSpawn
"""
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./price_tracker.db")

# Configuración específica para SQLite
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    echo=os.getenv("DEBUG", "False") == "True",
    connect_args=connect_args
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class User(Base):
    """Modelo de usuario para autenticación"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    email_verified = Column(Boolean, default=False)
    dark_mode = Column(Boolean, default=False)  # Preferencia de tema
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    productos = relationship("Producto", back_populates="user", cascade="all, delete-orphan")
    email_verifications = relationship("EmailVerification", back_populates="user", cascade="all, delete-orphan")


class Producto(Base):
    """Modelo de producto rastreado"""
    __tablename__ = "productos"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    nombre = Column(String, nullable=False)
    url = Column(String, nullable=False)
    precio_actual = Column(Float, nullable=True)
    precio_objetivo = Column(Float, nullable=True)
    tienda = Column(String, nullable=True)  # Amazon, MercadoLibre, etc.
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    user = relationship("User", back_populates="productos")
    historial = relationship("HistorialPrecio", back_populates="producto", cascade="all, delete-orphan")


class HistorialPrecio(Base):
    """Modelo de historial de precios"""
    __tablename__ = "historial_precios"
    
    id = Column(Integer, primary_key=True, index=True)
    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False, index=True)
    precio = Column(Float, nullable=False)
    fecha = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relaciones
    producto = relationship("Producto", back_populates="historial")


class EmailVerification(Base):
    """Modelo de verificación de email"""
    __tablename__ = "email_verifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    code = Column(String(6), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    is_used = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relaciones
    user = relationship("User", back_populates="email_verifications")


class Feedback(Base):
    """Modelo de feedback de usuarios"""
    __tablename__ = "feedback"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    email = Column(String, nullable=True)
    mensaje = Column(String, nullable=False)
    rating = Column(Integer, nullable=True)  # 1-5 estrellas
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relación
    user = relationship("User")


def get_db():
    """Dependency para obtener sesión de base de datos"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Inicializar base de datos y crear todas las tablas"""
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully")


if __name__ == "__main__":
    init_db()
