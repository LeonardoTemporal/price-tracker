"""
Script para recrear la base de datos con la estructura correcta
Author: HellSpawn
"""
import os
import sys
import time

# Eliminar base de datos si existe
db_path = "price_tracker.db"
if os.path.exists(db_path):
    print(f"Intentando eliminar {db_path}...")
    max_intentos = 5
    for intento in range(max_intentos):
        try:
            os.remove(db_path)
            print("Base de datos eliminada exitosamente")
            break
        except PermissionError:
            if intento < max_intentos - 1:
                print(f"Intento {intento + 1}: Archivo en uso, esperando 2 segundos...")
                time.sleep(2)
            else:
                print("ERROR: No se pudo eliminar la base de datos.")
                print("Por favor cierra todas las terminales de Python y ejecuta este script de nuevo")
                sys.exit(1)
else:
    print("No existe base de datos previa")

# Importar y crear tablas
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from backend.app.database import Base, engine

print("Creando nuevas tablas...")
Base.metadata.create_all(bind=engine)
print("¡Base de datos creada exitosamente con la estructura correcta!")
print("\nTablas creadas:")
for table in Base.metadata.tables.keys():
    print(f"  - {table}")
