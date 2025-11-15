"""
Script de migración para agregar columnas faltantes
Ejecutar en producción para actualizar la base de datos sin perder datos

Author: HellSpawn
"""
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("ERROR: DATABASE_URL no está configurada")
    exit(1)

engine = create_engine(DATABASE_URL)

# Migraciones a ejecutar
migrations = [
    # Agregar columnas a users si no existen
    """
    DO $$ 
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                      WHERE table_name='users' AND column_name='email_verified') THEN
            ALTER TABLE users ADD COLUMN email_verified BOOLEAN DEFAULT FALSE;
            RAISE NOTICE 'Columna email_verified agregada';
        ELSE
            RAISE NOTICE 'Columna email_verified ya existe';
        END IF;
    END $$;
    """,
    """
    DO $$ 
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                      WHERE table_name='users' AND column_name='dark_mode') THEN
            ALTER TABLE users ADD COLUMN dark_mode BOOLEAN DEFAULT FALSE;
            RAISE NOTICE 'Columna dark_mode agregada';
        ELSE
            RAISE NOTICE 'Columna dark_mode ya existe';
        END IF;
    END $$;
    """,
    # Agregar columna tienda a productos si no existe
    """
    DO $$ 
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                      WHERE table_name='productos' AND column_name='tienda') THEN
            ALTER TABLE productos ADD COLUMN tienda VARCHAR;
            RAISE NOTICE 'Columna tienda agregada';
        ELSE
            RAISE NOTICE 'Columna tienda ya existe';
        END IF;
    END $$;
    """,
    # Crear tabla email_verifications si no existe
    """
    CREATE TABLE IF NOT EXISTS email_verifications (
        id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        code VARCHAR(6) NOT NULL,
        expires_at TIMESTAMP NOT NULL,
        is_used BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """,
    # Crear índice si no existe
    """
    DO $$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'ix_email_verifications_user_id') THEN
            CREATE INDEX ix_email_verifications_user_id ON email_verifications(user_id);
            RAISE NOTICE 'Índice ix_email_verifications_user_id creado';
        ELSE
            RAISE NOTICE 'Índice ix_email_verifications_user_id ya existe';
        END IF;
    END $$;
    """,
    # Crear tabla feedback si no existe
    """
    CREATE TABLE IF NOT EXISTS feedback (
        id SERIAL PRIMARY KEY,
        user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
        email VARCHAR,
        mensaje TEXT NOT NULL,
        rating INTEGER CHECK (rating >= 1 AND rating <= 5),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """,
    # Crear índice si no existe
    """
    DO $$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'ix_feedback_user_id') THEN
            CREATE INDEX ix_feedback_user_id ON feedback(user_id);
            RAISE NOTICE 'Índice ix_feedback_user_id creado';
        ELSE
            RAISE NOTICE 'Índice ix_feedback_user_id ya existe';
        END IF;
    END $$;
    """
]

def run_migrations():
    """Ejecutar todas las migraciones"""
    print("Iniciando migraciones...")
    print(f"Database: {DATABASE_URL[:50]}...")
    
    with engine.connect() as conn:
        for i, migration in enumerate(migrations, 1):
            try:
                print(f"\n[{i}/{len(migrations)}] Ejecutando migración...")
                result = conn.execute(text(migration))
                conn.commit()
                print(f"✓ Migración {i} completada")
            except Exception as e:
                print(f"✗ Error en migración {i}: {str(e)}")
                conn.rollback()
    
    print("\n¡Migraciones completadas!")

if __name__ == "__main__":
    run_migrations()
