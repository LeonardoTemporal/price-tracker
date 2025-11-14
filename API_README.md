# Price Tracker API v3.0

API REST profesional para rastreo de precios de productos en línea con autenticación JWT y soporte multi-usuario.

## Desarrollador

**HellSpawn**

Sistema desarrollado como proyecto profesional de rastreo de precios con arquitectura moderna y escalable.

## Características

- Sistema de autenticación JWT seguro
- Soporte multi-usuario con aislamiento de datos
- Web scraping inteligente para múltiples sitios
- Historial completo de precios
- Sistema de alertas por precio objetivo
- Base de datos PostgreSQL con Supabase
- Documentación interactiva con Swagger UI
- API RESTful siguiendo mejores prácticas

## Tecnologías

- **FastAPI 0.104.1**: Framework web moderno y rápido
- **PostgreSQL**: Base de datos relacional en Supabase
- **SQLAlchemy 2.0.44**: ORM para manejo de base de datos
- **JWT (python-jose)**: Autenticación con tokens
- **bcrypt**: Hash seguro de contraseñas
- **BeautifulSoup4**: Web scraping
- **Pydantic**: Validación de datos

## Documentación

### Ver documentación interactiva

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Despliegue en producción

Una vez desplegado, la documentación estará disponible públicamente en:
- `https://tu-dominio.com/docs`
- `https://tu-dominio.com/redoc`

## Endpoints Principales

### Autenticación

- `POST /api/auth/register` - Registrar nuevo usuario
- `POST /api/auth/login` - Iniciar sesión (obtener token JWT)
- `GET /api/auth/me` - Obtener información del usuario actual

### Productos (Requieren autenticación)

- `GET /api/productos/` - Listar todos los productos del usuario
- `GET /api/productos/{id}` - Obtener producto específico
- `POST /api/productos/` - Crear nuevo producto
- `PUT /api/productos/{id}` - Actualizar producto
- `DELETE /api/productos/{id}` - Eliminar producto
- `POST /api/productos/{id}/actualizar-precio` - Actualizar precio manualmente
- `POST /api/productos/actualizar-todos` - Actualizar todos los productos
- `POST /api/productos/test-url` - Probar si una URL es compatible

### Estadísticas

- `GET /api/productos/estadisticas/resumen` - Obtener resumen de estadísticas

## Autenticación

Esta API utiliza JWT (JSON Web Tokens) para autenticación.

### Flujo de autenticación:

1. **Registrarse**: Envía una petición POST a `/api/auth/register` con:
   ```json
   {
     "email": "usuario@ejemplo.com",
     "username": "usuario",
     "password": "contraseña123"
   }
   ```

2. **Iniciar sesión**: Envía una petición POST a `/api/auth/login` con:
   ```json
   {
     "username": "usuario",
     "password": "contraseña123"
   }
   ```
   
   Recibirás una respuesta con el token:
   ```json
   {
     "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
     "token_type": "Bearer",
     "user": { ... }
   }
   ```

3. **Usar el token**: Incluye el token en el header de tus peticiones:
   ```
   Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
   ```

## Ejemplos de uso

### Registrar usuario (cURL)

```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@test.com",
    "username": "testuser",
    "password": "test123456"
  }'
```

### Iniciar sesión (cURL)

```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=test123456"
```

### Añadir producto (cURL)

```bash
curl -X POST "http://localhost:8000/api/productos/" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Producto de prueba",
    "url": "https://www.mercadolibre.com.mx/...",
    "precio_objetivo": 1500.00
  }'
```

### Listar productos (cURL)

```bash
curl -X GET "http://localhost:8000/api/productos/" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## Sitios Web Soportados

El scraper tiene configuraciones específicas para:

- **MercadoLibre**: Totalmente compatible
- **Amazon**: Múltiples selectores
- **eBay**: Soporte específico
- **Genérico**: Funciona con la mayoría de tiendas en línea

## Despliegue

### Variables de entorno requeridas

```env
DATABASE_URL=postgresql://user:pass@host:5432/dbname
SECRET_KEY=tu-clave-secreta-de-256-bits
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
ALLOWED_ORIGINS=https://tu-frontend.com
DEBUG=False
```

### Recomendaciones de hosting

- **Railway**: https://railway.app (Gratis, fácil)
- **Render**: https://render.com (Gratis, confiable)
- **Fly.io**: https://fly.io (Gratis hasta cierto límite)

## Exportar Documentación

Puedes exportar la documentación OpenAPI como JSON:

```bash
python export_api_docs.py
```

Esto generará `api_documentation.json` que puedes:
1. Subir a tu repositorio de GitHub
2. Visualizar en https://editor.swagger.io/
3. Importar en Postman o Insomnia

## Seguridad

- Contraseñas hasheadas con bcrypt (cost factor 12)
- Tokens JWT con expiración de 30 minutos
- Secret key de 256 bits
- CORS configurado
- Validación de datos con Pydantic
- SQLAlchemy ORM previene SQL injection
- Aislamiento de datos por usuario

## Licencia

MIT License

## Contribuciones

Proyecto educativo y profesional. Sugerencias y mejoras son bienvenidas.

---

Desarrollado con FastAPI, PostgreSQL y buenas prácticas de desarrollo backend.
