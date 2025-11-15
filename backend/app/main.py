"""
FastAPI Application - Price Tracker Backend v3.0
API REST con autenticación JWT y PostgreSQL

Author: HellSpawn
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import sys
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Añadir el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.app.routers import auth, productos_auth, feedback
from backend.app.database import init_db


# Configuración de eventos de inicio/cierre
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Iniciando Price Tracker API v3.0 con autenticación...")
    print("Inicializando base de datos...")
    init_db()
    print("Base de datos lista")
    yield
    # Shutdown
    print("Cerrando Price Tracker API...")


# Crear aplicación FastAPI
app = FastAPI(
    title="Price Tracker API",
    description="""
    ## API REST para rastrear precios de productos en línea
    
    Sistema multi-usuario con autenticación JWT que permite:
    - Rastrear precios de productos de diferentes tiendas en línea
    - Historial completo de cambios de precios
    - Alertas cuando se alcanza el precio objetivo
    - Gráficos de evolución de precios
    - Soporte para múltiples sitios web (MercadoLibre, Amazon, eBay, etc.)
    
    ### Autenticación
    Esta API utiliza JWT (JSON Web Tokens) para autenticación. Para usar los endpoints protegidos:
    1. Registra un usuario en `/api/auth/register`
    2. Inicia sesión en `/api/auth/login` para obtener tu token
    3. Usa el token en el header: `Authorization: Bearer {token}`
    
    ### Tecnologías
    - FastAPI 0.104.1
    - PostgreSQL (Supabase)
    - SQLAlchemy 2.0.44
    - JWT Authentication
    - bcrypt password hashing
    - BeautifulSoup4 web scraping
    
    ### Desarrollador
    **HellSpawn**
    
    Sistema desarrollado como proyecto profesional de rastreo de precios con arquitectura moderna y escalable.
    
    ### Enlaces
    - Documentación interactiva: `/docs`
    - Documentación alternativa: `/redoc`
    - GitHub: [Próximamente]
    """,
    version="3.0.0",
    contact={
        "name": "HellSpawn",
        "email": "hellspawn@pricetracker.dev"
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT"
    },
    lifespan=lifespan
)

# Obtener orígenes permitidos desde .env
allowed_origins = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:5173,http://localhost:5174,http://localhost:3000"
).split(",")

# Limpiar espacios en blanco de cada origen
allowed_origins = [origin.strip() for origin in allowed_origins]

# Configurar CORS - Debe ir ANTES de definir las rutas
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)


# Ruta raíz
@app.get("/")
async def root():
    return {
        "message": "Price Tracker API",
        "version": "3.0.0",
        "features": ["JWT Authentication", "Multi-user", "PostgreSQL"],
        "docs": "/docs",
        "status": "running"
    }


# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "3.0.0"}


# Incluir routers
app.include_router(auth.router, prefix="/api")
app.include_router(productos_auth.router, prefix="/api")
app.include_router(feedback.router, prefix="/api")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
