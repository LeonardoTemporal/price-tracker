# Price Tracker v3.0 - Multi-usuario con Autenticación

**Aplicación Full-Stack profesional** para rastrear precios de productos en línea con sistema de autenticación JWT, multi-usuario, alertas inteligentes e historial visual.

## Novedades v3.0

- Sistema de autenticación JWT completo
- Multi-usuario: cada usuario tiene sus propios productos
- Base de datos con SQLAlchemy ORM
- Compatible con PostgreSQL y SQLite
- Seguridad mejorada con bcrypt
- Rutas protegidas en frontend
- Interceptores Axios para tokens
- Sesiones persistentes

## Stack Tecnológico

### Backend
- **FastAPI**: Framework moderno para API REST
- **SQLAlchemy**: ORM para manejo de base de datos
- **PostgreSQL/SQLite**: Base de datos relacional
- **JWT**: Autenticación con tokens
- **Bcrypt**: Hash seguro de contraseñas
- **Pydantic**: Validación de datos

### Frontend
- **React 18**: Biblioteca UI moderna
- **React Router**: Navegación y rutas protegidas
- **Context API**: Gestión de estado de autenticación
- **TailwindCSS**: Estilos utility-first
- **React Query**: Gestión de estado del servidor
- **Recharts**: Gráficos interactivos
- **Axios**: Cliente HTTP con interceptores

## Instalación Rápida

### 1. Instalar Dependencias Backend

```cmd
cd c:\Users\leoac\Documents\School\Coding\ProyectosPersonales\RastreadorPrecios
.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
```

### 2. Configurar Base de Datos

Tienes dos opciones:

**Opción A: SQLite (Desarrollo Local - Recomendado para empezar)**
- Ya está configurado por defecto en `.env`
- No requiere instalación adicional
- Perfecto para desarrollo y pruebas

**Opción B: PostgreSQL (Producción)**
- Lee la guía completa en `POSTGRESQL_SETUP.md`
- Opciones: Instalación local, Docker, o nube (Supabase/Railway)
- Actualiza el `DATABASE_URL` en `.env`

### 3. Inicializar Base de Datos

```cmd
.venv\Scripts\python.exe -m backend.app.database
```

Esto creará automáticamente las tablas:
- `users` (usuarios con autenticación)
- `productos` (productos por usuario)
- `historial_precios` (precios históricos)

### 4. Iniciar la Aplicación

**Opción 1: Script Automático**
```cmd
start-all.bat
```

**Opción 2: Manual**

Backend:
```cmd
.venv\Scripts\python.exe -m uvicorn backend.app.main:app --reload
```

Frontend:
```cmd
cd frontend
npm install
npm run dev
```

## URLs Importantes

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs (Swagger)**: http://localhost:8000/docs
- **API Redoc**: http://localhost:8000/redoc

## Cómo Usar

### 1. Crear Cuenta

1. Abre http://localhost:5173/register
2. Completa el formulario:
   - Email válido
   - Usuario (mínimo 3 caracteres)
   - Contraseña (mínimo 6 caracteres)
3. Serás redirigido automáticamente al dashboard

### 2. Iniciar Sesión

1. Ve a http://localhost:5173/login
2. Usa tu usuario/email y contraseña
3. El token JWT se guarda automáticamente
4. Accede a todas las funcionalidades

### 3. Añadir Productos

1. Click en "Añadir" en la navegación
2. Ingresa nombre y URL del producto
3. (Opcional) Establece precio objetivo
4. Prueba la URL antes de guardar
5. Los productos son privados para tu cuenta

### 4. Monitorear Precios

- Ver todos tus productos en la lista
- Gráficos de evolución de precios
- Alertas cuando se alcanza el precio objetivo
- Actualización manual o automática

### 5. Cerrar Sesión

- Click en "Salir" en la barra superior
- Tu token se elimina y debes volver a iniciar sesión

## Variables de Entorno (.env)

```env
# Base de Datos
DATABASE_URL=sqlite:///./price_tracker.db
# O para PostgreSQL:
# DATABASE_URL=postgresql://user:password@localhost:5432/price_tracker

# JWT Configuration
SECRET_KEY=tu-clave-secreta-aqui
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000

# App
DEBUG=True
```

**IMPORTANTE**: Cambia el `SECRET_KEY` en producción. Genera uno con:
```python
python -c "import secrets; print(secrets.token_hex(32))"
```

## Estructura del Proyecto

```
RastreadorPrecios/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app con autenticación
│   │   ├── database.py          # Modelos SQLAlchemy
│   │   ├── security.py          # JWT y password hashing
│   │   ├── schemas.py           # Validación Pydantic
│   │   └── routers/
│   │       ├── auth.py          # Login/Register endpoints
│   │       └── productos_auth.py # Productos con auth
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── contexts/
│   │   │   └── AuthContext.jsx  # Estado global de auth
│   │   ├── components/
│   │   │   ├── Login.jsx        # Página de login
│   │   │   ├── Register.jsx     # Página de registro
│   │   │   ├── ProtectedRoute.jsx # HOC para rutas
│   │   │   ├── Layout.jsx       # Nav con user info
│   │   │   ├── Dashboard.jsx
│   │   │   ├── ProductList.jsx
│   │   │   ├── ProductDetail.jsx
│   │   │   └── AddProduct.jsx
│   │   ├── services/
│   │   │   └── api.js          # Axios con interceptores
│   │   ├── App.jsx             # Rutas protegidas
│   │   └── main.jsx            # AuthProvider
│   └── package.json
│
├── src/                        # Lógica compartida
│   ├── scraper.py
│   └── ...
│
├── .env                        # Variables de entorno
├── .env.example               # Template de variables
├── .gitignore                 # Excluye .env y secrets
├── POSTGRESQL_SETUP.md        # Guía de PostgreSQL
└── README.md
```

## API Endpoints

### Autenticación
- `POST /api/auth/register` - Registrar usuario
- `POST /api/auth/login` - Iniciar sesión (obtener token)
- `GET /api/auth/me` - Obtener usuario actual (requiere token)

### Productos (Requieren Autenticación)
- `GET /api/productos/` - Listar productos del usuario
- `GET /api/productos/{id}` - Obtener producto específico
- `POST /api/productos/` - Crear producto
- `PUT /api/productos/{id}` - Actualizar producto
- `DELETE /api/productos/{id}` - Eliminar producto
- `POST /api/productos/{id}/actualizar-precio` - Actualizar precio
- `POST /api/productos/actualizar-todos` - Actualizar todos
- `POST /api/productos/test-url` - Probar URL
- `GET /api/productos/estadisticas/resumen` - Estadísticas

## Seguridad

- Contraseñas hasheadas con bcrypt (cost factor 12)
- Tokens JWT con expiración de 30 minutos
- Secret key de 256 bits
- CORS configurado para orígenes permitidos
- Validación de datos con Pydantic
- SQLAlchemy ORM previene SQL injection
- Headers de autorización Bearer
- Rutas protegidas en frontend y backend

## Migración de PostgreSQL

Si quieres migrar de SQLite a PostgreSQL:

1. **Instala PostgreSQL** (ver `POSTGRESQL_SETUP.md`)

2. **Actualiza `.env`**:
```env
DATABASE_URL=postgresql://postgres:tu_password@localhost:5432/price_tracker
```

3. **Reinicia el backend**:
```cmd
.venv\Scripts\python.exe -m uvicorn backend.app.main:app --reload
```

4. **Las tablas se crean automáticamente**

## Despliegue a Producción

### Backend (Railway/Render/DigitalOcean)

1. Conecta tu repositorio Git
2. Configura variables de entorno:
   ```
   DATABASE_URL=postgresql://...
   SECRET_KEY=nuevo-secreto-generado
   ALLOWED_ORIGINS=https://tu-frontend.com
   DEBUG=False
   ```
3. Comando de inicio: `uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`

### Frontend (Vercel/Netlify)

1. Conecta tu repositorio
2. Directorio: `frontend`
3. Build command: `npm run build`
4. Output directory: `dist`
5. Variable de entorno: `VITE_API_URL=https://tu-backend.com/api`

### Base de Datos (Supabase/Railway)

1. Crea proyecto PostgreSQL
2. Copia la connection string
3. Pégala en `DATABASE_URL` del backend

## Troubleshooting

### Error: "Token inválido o expirado"
- Tu sesión ha expirado, vuelve a iniciar sesión
- Los tokens duran 30 minutos por defecto

### Error: "Usuario ya existe"
- El email o username ya están registrados
- Prueba con otros valores

### Error: "Could not connect to database"
- Verifica que el `DATABASE_URL` en `.env` sea correcto
- Si usas PostgreSQL, verifica que esté corriendo

### Frontend no carga después del login
- Verifica que el backend esté corriendo
- Revisa la consola del navegador (F12)
- Verifica que CORS esté configurado correctamente

### La app no guarda productos
- Verifica que estés autenticado (token válido)
- Revisa los logs del backend
- Verifica que la base de datos tenga las tablas creadas

## Próximas Mejoras

- [ ] Refresh tokens para sesiones más largas
- [ ] Verificación de email
- [ ] Recuperación de contraseña
- [ ] Notificaciones por email
- [ ] Roles de usuario (admin, premium)
- [ ] Exportar datos a CSV
- [ ] Dark mode
- [ ] Aplicación móvil

## Contribuciones

Este proyecto está en desarrollo activo. Sugerencias y mejoras son bienvenidas.

## Licencia

Proyecto de código abierto para uso educativo y personal.

## Autor

**HellSpawn**

Desarrollado como proyecto de aprendizaje de autenticación JWT, FastAPI, React y desarrollo full-stack profesional.

---

**Price Tracker v3.0** - Sistema multi-usuario con autenticación segura

Disfruta rastreando precios de forma segura y privada.
