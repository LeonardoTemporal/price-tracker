"""
Script de migración de SQLite a PostgreSQL
Copia todos los datos de la base de datos actual a PostgreSQL

Author: HellSpawn
"""
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.database import User, Producto, HistorialPrecio, Base
import os
from dotenv import load_dotenv

load_dotenv()

def migrate_data(sqlite_url, postgresql_url):
    """
    Migra datos de SQLite a PostgreSQL
    
    Args:
        sqlite_url: URL de conexión a SQLite
        postgresql_url: URL de conexión a PostgreSQL
    """
    print("Iniciando migración de datos...")
    print(f"Origen (SQLite): {sqlite_url}")
    print(f"Destino (PostgreSQL): {postgresql_url[:50]}...")
    
    # Conectar a SQLite (origen)
    print("\n1. Conectando a SQLite...")
    sqlite_engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})
    SQLiteSession = sessionmaker(bind=sqlite_engine)
    sqlite_session = SQLiteSession()
    
    # Conectar a PostgreSQL (destino)
    print("2. Conectando a PostgreSQL...")
    try:
        postgresql_engine = create_engine(postgresql_url, pool_pre_ping=True)
        PostgreSQLSession = sessionmaker(bind=postgresql_engine)
        postgresql_session = PostgreSQLSession()
        
        # Crear tablas en PostgreSQL
        print("3. Creando tablas en PostgreSQL...")
        Base.metadata.create_all(bind=postgresql_engine)
        print("   Tablas creadas exitosamente")
        
    except Exception as e:
        print(f"\nError al conectar a PostgreSQL: {e}")
        print("\nVerifica que:")
        print("1. PostgreSQL esté corriendo")
        print("2. La base de datos exista")
        print("3. Las credenciales sean correctas")
        print("4. El formato de DATABASE_URL sea correcto")
        sqlite_session.close()
        return False
    
    try:
        # Migrar usuarios
        print("\n4. Migrando usuarios...")
        users = sqlite_session.query(User).all()
        user_map = {}  # Mapeo de IDs antiguos a nuevos
        
        for old_user in users:
            # Verificar si el usuario ya existe
            existing_user = postgresql_session.query(User).filter(
                (User.email == old_user.email) | (User.username == old_user.username)
            ).first()
            
            if existing_user:
                print(f"   Usuario '{old_user.username}' ya existe, usando el existente")
                user_map[old_user.id] = existing_user.id
            else:
                new_user = User(
                    email=old_user.email,
                    username=old_user.username,
                    hashed_password=old_user.hashed_password,
                    is_active=old_user.is_active,
                    created_at=old_user.created_at,
                    updated_at=old_user.updated_at
                )
                postgresql_session.add(new_user)
                postgresql_session.flush()  # Para obtener el ID
                user_map[old_user.id] = new_user.id
                print(f"   Usuario '{old_user.username}' migrado")
        
        postgresql_session.commit()
        print(f"   Total usuarios migrados: {len(users)}")
        
        # Migrar productos
        print("\n5. Migrando productos...")
        productos = sqlite_session.query(Producto).all()
        producto_map = {}  # Mapeo de IDs antiguos a nuevos
        
        for old_producto in productos:
            new_producto = Producto(
                user_id=user_map[old_producto.user_id],
                nombre=old_producto.nombre,
                url=old_producto.url,
                precio_actual=old_producto.precio_actual,
                precio_objetivo=old_producto.precio_objetivo,
                created_at=old_producto.created_at,
                updated_at=old_producto.updated_at
            )
            postgresql_session.add(new_producto)
            postgresql_session.flush()
            producto_map[old_producto.id] = new_producto.id
            print(f"   Producto '{old_producto.nombre}' migrado")
        
        postgresql_session.commit()
        print(f"   Total productos migrados: {len(productos)}")
        
        # Migrar historial de precios
        print("\n6. Migrando historial de precios...")
        historiales = sqlite_session.query(HistorialPrecio).all()
        
        for old_historial in historiales:
            new_historial = HistorialPrecio(
                producto_id=producto_map[old_historial.producto_id],
                precio=old_historial.precio,
                fecha=old_historial.fecha
            )
            postgresql_session.add(new_historial)
        
        postgresql_session.commit()
        print(f"   Total registros de historial migrados: {len(historiales)}")
        
        print("\n" + "="*60)
        print("MIGRACIÓN COMPLETADA EXITOSAMENTE")
        print("="*60)
        print(f"\nResumen:")
        print(f"  - Usuarios migrados: {len(users)}")
        print(f"  - Productos migrados: {len(productos)}")
        print(f"  - Registros de historial: {len(historiales)}")
        print("\nAhora puedes:")
        print("1. Actualizar DATABASE_URL en .env a la URL de PostgreSQL")
        print("2. Reiniciar el backend")
        print("3. Verificar que todo funcione correctamente")
        
        return True
        
    except Exception as e:
        print(f"\nError durante la migración: {e}")
        postgresql_session.rollback()
        return False
        
    finally:
        sqlite_session.close()
        postgresql_session.close()


def main():
    """Función principal"""
    print("="*60)
    print("MIGRACIÓN DE SQLite A PostgreSQL")
    print("="*60)
    
    # Obtener URLs de conexión
    sqlite_url = "sqlite:///./price_tracker.db"
    
    postgresql_url = os.getenv("POSTGRESQL_URL")
    if not postgresql_url:
        print("\nNo se encontró POSTGRESQL_URL en .env")
        print("\nPor favor, añade la siguiente línea a tu archivo .env:")
        print("POSTGRESQL_URL=postgresql://usuario:contraseña@host:puerto/database")
        print("\nEjemplo para Supabase:")
        print("POSTGRESQL_URL=postgresql://postgres:tu_password@db.xxx.supabase.co:5432/postgres")
        print("\nEjemplo para local:")
        print("POSTGRESQL_URL=postgresql://postgres:postgres@localhost:5432/price_tracker")
        return
    
    # Confirmar migración
    print(f"\nOrigen: {sqlite_url}")
    print(f"Destino: {postgresql_url[:50]}...")
    
    respuesta = input("\n¿Deseas continuar con la migración? (si/no): ").lower()
    if respuesta not in ['si', 's', 'yes', 'y']:
        print("Migración cancelada")
        return
    
    # Ejecutar migración
    success = migrate_data(sqlite_url, postgresql_url)
    
    if success:
        print("\n" + "="*60)
        print("SIGUIENTE PASO:")
        print("="*60)
        print("\n1. Abre el archivo .env")
        print("2. Cambia la línea:")
        print(f"   DATABASE_URL=sqlite:///./price_tracker.db")
        print("   Por:")
        print(f"   DATABASE_URL={postgresql_url}")
        print("\n3. Reinicia el backend")
        print("\n4. Opcional: Renombra price_tracker.db a price_tracker.db.backup")
    else:
        print("\nLa migración falló. Revisa los errores arriba.")
        print("Tu base de datos SQLite no ha sido modificada.")


if __name__ == "__main__":
    main()

