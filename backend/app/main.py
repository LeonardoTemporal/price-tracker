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
    # Startup: inicializar base de datos y ejecutar migraciones
    print("Iniciando Price Tracker API v3.0 con autenticación...")
    print("Inicializando base de datos...")
    init_db()
    print("Ejecutando migraciones de base de datos...")
    from sqlalchemy import text
    from backend.app.database import engine
    try:
        with engine.connect() as conn:
            # Agregar email_verified si no existe
            conn.execute(text("""
                DO $$ 
                BEGIN
                    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                  WHERE table_name='users' AND column_name='email_verified') THEN
                        ALTER TABLE users ADD COLUMN email_verified BOOLEAN DEFAULT FALSE;
                    END IF;
                END $$;
            """))
            # Agregar dark_mode si no existe
            conn.execute(text("""
                DO $$ 
                BEGIN
                    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                  WHERE table_name='users' AND column_name='dark_mode') THEN
                        ALTER TABLE users ADD COLUMN dark_mode BOOLEAN DEFAULT FALSE;
                    END IF;
                END $$;
            """))
            # Agregar tienda si no existe
            conn.execute(text("""
                DO $$ 
                BEGIN
                    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                  WHERE table_name='productos' AND column_name='tienda') THEN
                        ALTER TABLE productos ADD COLUMN tienda VARCHAR;
                    END IF;
                END $$;
            """))
            conn.commit()
            print("Migraciones completadas exitosamente")
    except Exception as e:
        print(f"Error en migraciones: {str(e)}")
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
allowed_origins_str = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:5173,http://localhost:5174,http://localhost:3000"
)
allowed_origins = [origin.strip() for origin in allowed_origins_str.split(",")]

# Agregar origins comunes para desarrollo y producción
development_origins = [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",
    "http://127.0.0.1:3000"
]

for origin in development_origins:
    if origin not in allowed_origins:
        allowed_origins.append(origin)

print(f"🌐 CORS allowed origins: {allowed_origins}")  # Debug

# Configurar CORS - Debe ir ANTES de definir las rutas
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
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
