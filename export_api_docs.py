"""
Script para exportar la documentación de la API en formato OpenAPI JSON
Author: HellSpawn
"""
import json
from backend.app.main import app

# Obtener el esquema OpenAPI
openapi_schema = app.openapi()

# Guardar en archivo JSON
with open("api_documentation.json", "w", encoding="utf-8") as f:
    json.dump(openapi_schema, f, indent=2, ensure_ascii=False)

print("Documentación exportada exitosamente a 'api_documentation.json'")
print("\nPuedes:")
print("1. Subirlo a tu repositorio de GitHub")
print("2. Visualizarlo en https://editor.swagger.io/")
print("3. Usar Swagger UI para crear una página HTML estática")
