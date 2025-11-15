# Price Tracker v3.0

Aplicación web profesional de rastreo de precios con autenticación multi-usuario, diseño responsive y alertas inteligentes. Rastrea productos en línea, visualiza historial de precios y recibe notificaciones cuando alcancen tu precio objetivo.

## Stack Tecnológico

### Backend
- **FastAPI 0.104.1**: Framework moderno y rápido para API REST
- **Python 3.8+**: Lógica de negocio y web scraping
- **SQLite + SQLAlchemy 2.0.44**: Base de datos con ORM avanzado
- **BeautifulSoup4**: Web scraping inteligente
- **JWT (python-jose 3.5.0)**: Autenticación con JSON Web Tokens
- **bcrypt 5.0.0**: Hash seguro de contraseñas
- **Pydantic**: Validación de datos y modelos

### Frontend
- **React 18**: Biblioteca UI moderna
- **Vite 5.4.21**: Build tool ultra-rápido con HMR
- **TailwindCSS 3.x**: Estilos utility-first con diseño responsive
- **React Query (TanStack Query)**: Gestión de estado del servidor
- **React Router**: Navegación SPA
- **Recharts**: Gráficos interactivos de línea
- **Axios**: Cliente HTTP con interceptores
- **Lucide React**: Iconos modernos y escalables
- **date-fns**: Manipulación y formateo de fechas

## Características

### Autenticación y Seguridad
- **Sistema de usuarios**: Registro e inicio de sesión con JWT
- **Contraseñas seguras**: Hash con bcrypt y salt
- **Sesiones persistentes**: Token guardado en localStorage
- **Rutas protegidas**: Middleware de autenticación en todas las rutas privadas
- **Aislamiento de datos**: Cada usuario solo ve sus productos

### Interfaz de Usuario
- **Diseño responsive**: Optimizado para móvil, tablet y desktop
- **Menú hamburguesa**: Navegación móvil intuitiva
- **Gráficos interactivos**: Visualiza la evolución de precios con Recharts
- **Dashboard informativo**: Resumen de productos, alertas y ahorro potencial
- **Botones táctiles**: Tamaños optimizados para pantallas touch (44px mínimo)
- **Tema moderno**: Interfaz limpia con TailwindCSS

### Funcionalidades
- **Sistema de alertas**: Notificaciones cuando se alcanza el precio objetivo
- **Actualización automática**: Actualiza precios de todos los productos con un clic
- **Historial completo**: Tabla detallada con todos los cambios de precio
- **Precio objetivo**: Establece el precio deseado y recibe alertas
- **Prueba de URL**: Verifica que el scraper puede extraer el precio antes de añadir
- **Actualización en tiempo real**: React Query mantiene los datos sincronizados
- **API REST completa**: Documentación automática con Swagger y ReDoc

### Performance
- **Carga rápida**: Vite con HMR para desarrollo y build optimizado
- **Queries eficientes**: React Query con caché inteligente
- **Backend asíncrono**: FastAPI con soporte async/await
- **Scraping inteligente**: Múltiples estrategias de extracción de precios

## Instalación Rápida

### Requisitos Previos
- Python 3.8 o superior
- Node.js 16 o superior
- npm o yarn

### Opción 1: Script Automático (Recomendado)

Simplemente ejecuta:

```cmd
start-all.bat
```

Este script:
1. Crea y activa el entorno virtual de Python
2. Instala las dependencias del backend
3. Instala las dependencias del frontend
4. Inicia el backend en puerto 8000
5. Inicia el frontend en puerto 5173
6. Abre ambos servicios en ventanas separadas

### Opción 2: Manual

#### 1. Backend
```cmd
# Crear entorno virtual
python -m venv .venv

# Activar entorno virtual
.venv\Scripts\activate

# Instalar dependencias
pip install -r backend/requirements.txt

# Iniciar servidor (con recarga automática)
python -m uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 2. Frontend
```cmd
# Navegar a la carpeta frontend
cd frontend

# Instalar dependencias
npm install

# Iniciar servidor de desarrollo
npm run dev
```

### Configuración de Red Local

Para acceder desde otros dispositivos en tu red local (como móviles):

1. Backend ya está configurado con `--host 0.0.0.0`
2. Frontend con flag `--host`:
```cmd
npm run dev -- --host
```
3. Obtén tu IP local: `ipconfig` (Windows) o `ifconfig` (Linux/Mac)
4. Accede desde cualquier dispositivo: `http://TU_IP_LOCAL:5173`
5. Crea archivo `.env.local` en `frontend/` con:
```
VITE_API_URL=http://TU_IP_LOCAL:8000/api
```

## URLs Importantes

Una vez iniciado:

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs (Swagger)**: http://localhost:8000/docs
- **API Redoc**: http://localhost:8000/redoc

## Estructura del Proyecto

```
RastreadorPrecios/
├── backend/                       # API Backend con FastAPI
│   ├── app/
│   │   ├── main.py               # Aplicación FastAPI principal con CORS
│   │   ├── database.py           # Modelos SQLAlchemy y sesión DB
│   │   ├── security.py           # JWT, bcrypt, autenticación
│   │   └── routers/              # Endpoints REST
│   │       ├── auth.py           # Registro, login, usuario actual
│   │       └── productos.py      # CRUD de productos con user_id
│   └── requirements.txt          # Dependencias Python
│
├── frontend/                      # Frontend React
│   ├── src/
│   │   ├── components/           # Componentes React
│   │   │   ├── Layout.jsx        # Nav con menú hamburguesa
│   │   │   ├── Login.jsx         # Formulario de login
│   │   │   ├── Register.jsx      # Formulario de registro
│   │   │   ├── Dashboard.jsx     # Dashboard responsive
│   │   │   ├── ProductList.jsx   # Lista de productos
│   │   │   ├── ProductDetail.jsx # Detalle con gráfico
│   │   │   └── AddProduct.jsx    # Añadir producto
│   │   ├── contexts/
│   │   │   └── AuthContext.jsx   # Estado global de auth
│   │   ├── services/
│   │   │   └── api.js            # Cliente Axios con interceptores
│   │   ├── App.jsx               # Rutas y protección
│   │   └── main.jsx              # Entry point
│   ├── .env.local                # Variables de entorno (API URL)
│   ├── package.json
│   ├── vite.config.js
│   └── tailwind.config.js        # Configuración de Tailwind
│
├── src/                           # Lógica de scraping compartida
│   ├── scraper.py                # Web scraping multi-sitio
│   ├── tracker.py                # Lógica de rastreo
│   └── database.py               # Helper de base de datos
│
├── price_tracker.db              # Base de datos SQLite
├── recreate_db.py                # Script para recrear DB
├── start-all.bat                 # Inicia backend + frontend
├── start-backend.bat             # Solo backend
├── start-frontend.bat            # Solo frontend
└── README.md
```

## Cómo Usar

### 1. Crear una Cuenta

1. Abre la aplicación en `http://localhost:5173`
2. Haz clic en **"Crear cuenta"**
3. Ingresa tu email, nombre de usuario y contraseña (mínimo 6 caracteres)
4. Serás redirigido automáticamente al dashboard

### 2. Iniciar Sesión

1. Ingresa tu nombre de usuario y contraseña
2. Tu sesión se mantendrá activa incluso si cierras el navegador

### 3. Añadir un Producto

1. Ve a la página **"Añadir"** desde el menú
2. Ingresa el nombre del producto
3. Pega la URL de la página del producto
4. (Opcional) Establece un precio objetivo para recibir alertas
5. Haz clic en **"Probar URL"** para verificar que el scraper funciona
6. Si la prueba es exitosa, haz clic en **"Añadir Producto"**

### 4. Ver y Gestionar Productos

1. Ve a **"Productos"** para ver todos tus productos en seguimiento
2. Haz clic en **"Actualizar Todos"** para obtener los precios actuales
3. Haz clic en **"Ver Detalles"** en cualquier producto para:
   - Ver el gráfico de evolución de precios
   - Consultar el historial completo con cambios
   - Actualizar el precio manualmente
   - Eliminar el producto

### 5. Monitorear Alertas en el Dashboard

1. En **"Inicio"** verás:
   - Tarjetas con total de productos, alertas activas y ahorro potencial
   - Lista de alertas (productos que alcanzaron tu precio objetivo)
   - Productos recientes con acceso rápido
   - Estadísticas visuales

## Sitios Web Compatibles

El scraper incluye configuraciones específicas optimizadas para:

### Sitios Soportados
- **Mercado Libre**: Totalmente compatible (probado y funcional)
- **Amazon**: Soporte para múltiples selectores de precio
- **eBay**: Configuración específica para sus elementos

### Extracción Genérica
Además de los sitios específicos, el scraper incluye métodos genéricos que funcionan con la mayoría de tiendas en línea que usan patrones comunes de HTML para mostrar precios.

### Cómo Funciona
1. **Detección de dominio**: Identifica el sitio web de la URL
2. **Selectores específicos**: Intenta con configuraciones personalizadas para ese dominio
3. **Fallback genérico**: Si falla, usa patrones de búsqueda genéricos en todo el HTML
4. **Limpieza inteligente**: Maneja diferentes formatos de números (1,234.56 o 1.234,56)

### Añadir Soporte para Nuevos Sitios

Edita `src/scraper.py` y añade una configuración en `domain_configs`:

```python
self.domain_configs = {
    'tu_tienda': {
        'selectors': [
            {'class': 'precio-clase'},
            {'id': 'precio-id'},
        ],
        'clean_pattern': r'[^\d,.]'
    }
}
```

**Consejo**: Usa la función **"Probar URL"** en la interfaz para verificar si un sitio es compatible antes de añadir el producto.

## Configuración Avanzada

### Variables de Entorno

Crea archivos `.env` para configuración personalizada:

#### Backend (`backend/.env`):
```
SECRET_KEY=tu-clave-secreta-super-segura-cambiar-en-produccion
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DATABASE_URL=sqlite:///./price_tracker.db
```

#### Frontend (`frontend/.env.local`):
```
VITE_API_URL=http://localhost:8000/api
```

### Base de Datos

La estructura de la base de datos SQLAlchemy incluye:

#### Tabla `users`
- id (Primary Key)
- email (Unique, Indexed)
- username (Unique, Indexed)
- hashed_password
- is_active
- created_at
- updated_at

#### Tabla `productos`
- id (Primary Key)
- user_id (Foreign Key a users)
- nombre
- url
- precio_actual
- precio_objetivo
- created_at
- updated_at

#### Tabla `historial_precios`
- id (Primary Key)
- producto_id (Foreign Key a productos)
- precio
- fecha (Indexed)

### Recrear Base de Datos

Si necesitas recrear la base de datos con el esquema correcto:

```cmd
python recreate_db.py
```

Este script elimina la base de datos antigua y crea una nueva con todas las tablas y relaciones correctas.

## Arquitectura del Sistema

### Capa de Presentación (Frontend - React SPA)
- **React Router**: Navegación cliente con rutas protegidas
- **Context API**: Estado global de autenticación
- **React Query**: Caché inteligente y sincronización con servidor
- **TailwindCSS**: Sistema de diseño responsive mobile-first
- **Componentes reutilizables**: Layout, formularios, cards, modales

### Capa de Aplicación (Backend - FastAPI)
- **Rutas protegidas**: Middleware de autenticación JWT en todas las rutas privadas
- **Separación de responsabilidades**: Routers para auth y productos
- **Dependency Injection**: FastAPI dependencies para DB y usuario actual
- **Validación automática**: Pydantic models y schemas
- **Documentación auto-generada**: Swagger UI y ReDoc

### Capa de Lógica de Negocio
- **Scraper multi-estrategia**: Configuraciones específicas + fallback genérico
- **Tracker**: Coordina scraping y almacenamiento
- **Seguridad**: bcrypt para passwords, JWT para sesiones
- **Manejo de errores**: Try-catch exhaustivos con logging

### Capa de Datos (Persistencia - SQLite + SQLAlchemy)
- **ORM**: SQLAlchemy 2.0 con modelos declarativos
- **Relaciones**: Foreign keys con cascading deletes
- **Índices**: Optimización en email, username, fecha
- **Migraciones**: Script de recreación de DB incluido

## Consideraciones Importantes

### Legal y Ético
1. **Respeta los términos de servicio** de los sitios web que rastreas
2. **No sobrecargues los servidores**: El scraper incluye timeout de 10 segundos
3. **Algunos sitios pueden bloquear scrapers**: Usa con moderación y responsabilidad
4. **Solo para uso personal**: No uses para scraping masivo o comercial

### Técnicas
1. **La estructura de los sitios cambia**: Los selectores pueden requerir actualizaciones
2. **User-Agent obligatorio**: El scraper simula un navegador real
3. **Timeout configurado**: Peticiones HTTP con límite de 10 segundos
4. **Caché del navegador**: React Query cachea datos para reducir peticiones

### Seguridad
1. **Cambia SECRET_KEY en producción**: La clave por defecto es solo para desarrollo
2. **HTTPS obligatorio en producción**: No uses HTTP para JWT en producción
3. **CORS configurado**: Actualmente permite todos los orígenes (solo desarrollo)
4. **Contraseñas seguras**: Mínimo 6 caracteres, considera aumentar a 8+

## Roadmap y Mejoras Futuras

### Funcionalidades
- [ ] Notificaciones push o email cuando se alcancen precios objetivo
- [ ] Exportación de datos a CSV/Excel
- [ ] Comparación de precios entre múltiples tiendas del mismo producto
- [ ] Historial de cambios en disponibilidad
- [ ] Predicción de precios con machine learning
- [ ] Categorías y etiquetas personalizadas
- [ ] Lista de deseos compartida

### Técnicas
- [ ] Migración a PostgreSQL para producción
- [ ] Scraping con Selenium para sitios con JavaScript
- [ ] Rate limiting por usuario
- [ ] Caché de precios con Redis
- [ ] Worker de Celery para actualización programada
- [ ] Soporte para más sitios web con configuraciones específicas
- [ ] Tests unitarios y de integración
- [ ] CI/CD con GitHub Actions

### Seguridad
- [ ] Refresh tokens para JWT
- [ ] Verificación de email
- [ ] Rate limiting de endpoints
- [ ] CAPTCHA en registro
- [ ] Logs de auditoría

### UX/UI
- [ ] Tema oscuro
- [ ] PWA (Progressive Web App) para instalación en móvil
- [ ] Notificaciones in-app
- [ ] Comparación visual de múltiples productos
- [ ] Filtros y búsqueda avanzada

## Solución de Problemas

### El backend no inicia
- Verifica que el entorno virtual esté activado
- Asegúrate de tener todas las dependencias: `pip install -r backend/requirements.txt`
- Revisa que el puerto 8000 no esté ocupado

### El frontend no inicia
- Ejecuta `npm install` en la carpeta frontend
- Verifica la versión de Node.js: debe ser 16+
- Revisa que el puerto 5173 no esté ocupado

### No puedo iniciar sesión
- Verifica que el backend esté corriendo
- Revisa la consola del navegador para errores de CORS
- Asegúrate de que el usuario existe (intenta registrarte de nuevo)

### El scraper no extrae el precio
- Usa la función "Probar URL" antes de añadir el producto
- Verifica que la URL sea accesible desde tu navegador
- Algunos sitios pueden bloquear bots o requerir cookies/sesión
- Revisa la consola del backend para logs detallados

### Error de base de datos
- Ejecuta `python recreate_db.py` para recrear la DB
- Cierra todas las aplicaciones que puedan tener la DB abierta
- Reinicia VS Code si el archivo está bloqueado

### No puedo acceder desde móvil
- Verifica que ambos dispositivos estén en la misma red WiFi
- Usa `ipconfig` para obtener tu IP local correcta
- Asegúrate de tener el archivo `.env.local` configurado en frontend
- Revisa que tu firewall permita conexiones en puertos 8000 y 5173

## 📄 Licencia

**Copyright © 2025 Leonardo Acosta (HellSpawn). Todos los Derechos Reservados.**

Este proyecto tiene **licencia propietaria**. El código es visible públicamente para fines de demostración, portafolio y referencia educativa.

**No se permite:**
- Copiar, modificar o distribuir el código
- Usar en proyectos comerciales o personales
- Crear trabajos derivados

Para uso educativo, colaboraciones o licenciamiento comercial, contacta a: **pricy.pricetracker@gmail.com**

Ver [LICENSE.md](LICENSE.md) para términos completos.

## 👨‍💻 Autor

**Leonardo Acosta (HellSpawn)**
- Email: pricy.pricetracker@gmail.com
- GitHub: [@LeonardoTemporal](https://github.com/LeonardoTemporal)

Desarrollado como proyecto profesional full-stack con React, FastAPI, autenticación JWT, verificación de email y diseño responsive.

## 🤝 Contribuciones

Este es un proyecto propietario. Si deseas contribuir o sugerir mejoras, por favor contacta al autor.

---

**Pricy Price Tracker** - Rastrea precios, ahorra dinero 🎯

Desarrollado con pasión por el desarrollo web moderno y la automatización.
