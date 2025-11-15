"""
Script para eliminar todos los usuarios de la base de datos
CUIDADO: Este script eliminará TODOS los usuarios y sus datos

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

def clear_all_users():
    """Eliminar todos los usuarios y datos relacionados"""
    print("⚠️  ADVERTENCIA: Esto eliminará TODOS los usuarios de la base de datos")
    print(f"Database: {DATABASE_URL[:50]}...")
    
    confirm = input("\n¿Estás seguro? Escribe 'SI' para confirmar: ")
    
    if confirm != "SI":
        print("Operación cancelada")
        return
    
    try:
        with engine.connect() as conn:
            # Obtener conteo actual
            result = conn.execute(text("SELECT COUNT(*) FROM users"))
            count = result.scalar()
            print(f"\nUsuarios actuales: {count}")
            
            if count == 0:
                print("No hay usuarios para eliminar")
                return
            
            # Eliminar en orden (CASCADE debería manejar esto, pero por si acaso)
            print("\n🗑️  Eliminando datos...")
            
            # Eliminar feedback
            result = conn.execute(text("DELETE FROM feedback"))
            print(f"✓ Feedback eliminado: {result.rowcount} registros")
            
            # Eliminar verificaciones de email
            result = conn.execute(text("DELETE FROM email_verifications"))
            print(f"✓ Verificaciones eliminadas: {result.rowcount} registros")
            
            # Eliminar historial de precios
            result = conn.execute(text("DELETE FROM historial_precios"))
            print(f"✓ Historial eliminado: {result.rowcount} registros")
            
            # Eliminar productos
            result = conn.execute(text("DELETE FROM productos"))
            print(f"✓ Productos eliminados: {result.rowcount} registros")
            
            # Eliminar usuarios
            result = conn.execute(text("DELETE FROM users"))
            print(f"✓ Usuarios eliminados: {result.rowcount} registros")
            
            conn.commit()
            
            print("\n✅ ¡Base de datos limpiada exitosamente!")
            print("Ahora puedes registrar nuevos usuarios con los mismos emails")
            
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    clear_all_users()
