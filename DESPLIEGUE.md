# Guía de Despliegue - Price Tracker v3.0

Esta guía te llevará paso a paso para desplegar tu aplicación en producción.

## Arquitectura de Despliegue

- **Backend (API)**: Fly.io (NO se duerme, gratis)
- **Frontend**: Vercel (Gratis ilimitado)
- **Base de Datos**: Supabase (Ya configurado)

## PASO 1: Preparar Repositorio en GitHub

### 1.1 Crear repositorio en GitHub

1. Ve a https://github.com/new
2. Nombre del repositorio: `price-tracker` (o el que prefieras)
3. Descripción: "Sistema profesional de rastreo de precios con autenticación JWT"
4. Selecciona **"Private"** o **"Public"** según prefieras
5. NO inicialices con README (ya lo tienes)
6. Haz clic en **"Create repository"**

### 1.2 Subir código a GitHub

En tu terminal, ejecuta estos comandos desde la raíz del proyecto:

```bash
git init
git add .
git commit -m "Initial commit - Price Tracker v3.0 con PostgreSQL"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/price-tracker.git
git push -u origin main
```

## PASO 2: Instalar Fly.io CLI

### 2.1 Instalar flyctl (CLI de Fly.io)

**En Windows (PowerShell como Administrador):**
```powershell
iwr https://fly.io/install.ps1 -useb | iex
```

Luego cierra y abre una nueva terminal para que funcione el comando `fly`.

**Verificar instalación:**
```bash
fly version
```

### 2.2 Crear cuenta y autenticarse

```bash
fly auth signup
```

O si ya tienes cuenta:
```bash
fly auth login
```

Esto abrirá tu navegador. Inicia sesión con GitHub y añade tu tarjeta de crédito para verificación (NO se te cobrará).

## PASO 3: Desplegar Backend en Fly.io

### 3.1 Lanzar la aplicación

Desde la raíz de tu proyecto, ejecuta:

```bash
fly launch
```

Fly.io te hará algunas preguntas:

1. **App Name**: Deja que genere uno o pon `price-tracker-api`
2. **Region**: Selecciona **Miami (mia)** (más cercano)
3. **PostgreSQL**: Di **NO** (ya tienes Supabase)
4. **Redis**: Di **NO**
5. **Deploy now**: Di **NO** (primero configuramos variables)

Esto creará el archivo `fly.toml` (ya está listo).

### 3.2 Configurar Variables de Entorno

Configura tus variables secretas con estos comandos:

```bash
fly secrets set DATABASE_URL="postgresql://postgres:Mayamini12345!@db.mlzuvcrtdxznfqnqqcet.supabase.co:5432/postgres"

fly secrets set SECRET_KEY="09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"

fly secrets set ALGORITHM="HS256"

fly secrets set ACCESS_TOKEN_EXPIRE_MINUTES="30"

fly secrets set DEBUG="False"

fly secrets set ALLOWED_ORIGINS="https://tu-frontend.vercel.app,http://localhost:5173"
```

**IMPORTANTE**: Después de desplegar el frontend, actualiza `ALLOWED_ORIGINS`.

### 3.3 Desplegar

```bash
fly deploy
```

Espera 2-3 minutos. Una vez listo, obten tu URL:

```bash
fly status
```

Tu API estará en: `https://price-tracker-api.fly.dev`

Prueba que funciona: `https://price-tracker-api.fly.dev/docs`

## PASO 4: Desplegar Frontend en Vercel

### 3.1 Preparar Frontend

Primero, actualiza la configuración del frontend para producción.

Crea el archivo `frontend/.env.production`:

```env
VITE_API_URL=https://TU-URL.railway.app/api
```

Reemplaza `price-tracker-api.fly.dev` con tu URL real de Fly.io.

### 3.2 Crear cuenta en Vercel

1. Ve a https://vercel.com
2. Haz clic en **"Sign Up"**
3. Inicia sesión con GitHub
4. Autoriza a Vercel

### 3.3 Desplegar Frontend

1. En Vercel, haz clic en **"Add New..."** → **"Project"**
2. Selecciona tu repositorio de GitHub `price-tracker`
3. Configura el proyecto:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
4. En **Environment Variables**, añade:
   ```
   VITE_API_URL = https://price-tracker-api.fly.dev/api
   ```
5. Haz clic en **"Deploy"**

### 3.4 Configurar Dominio (Opcional)

Vercel te da un dominio gratis como: `price-tracker.vercel.app`

Si quieres un dominio personalizado, ve a **"Settings"** → **"Domains"** en Vercel.

## PASO 5: Actualizar CORS en Backend

Ahora que tienes la URL de Vercel, actualiza ALLOWED_ORIGINS en Fly.io:

```bash
fly secrets set ALLOWED_ORIGINS="https://price-tracker.vercel.app,http://localhost:5173"
```

Fly.io redesplegará automáticamente con la nueva configuración.

## PASO 6: Verificar que Todo Funciona

### Backend
1. Ve a `https://price-tracker-api.fly.dev/docs`
2. Deberías ver la documentación de la API con tu nombre
3. Prueba el endpoint `/health`
4. **VENTAJA**: Tu API responde instantáneamente, NO se duerme

### Frontend
1. Ve a `https://price-tracker.vercel.app`
2. Regístrate con un nuevo usuario
3. Añade un producto
4. Verifica que se guarda correctamente

## PASO 7: Documentación Pública

Tu documentación API ahora está pública en:
- **Swagger UI**: `https://price-tracker-api.fly.dev/docs`
- **ReDoc**: `https://price-tracker-api.fly.dev/redoc`

Comparte estos links con quien quieras que vea la documentación.

## URLs Finales

Una vez desplegado, tendrás:

- **Frontend**: https://price-tracker.vercel.app
- **Backend API**: https://price-tracker-api.fly.dev
- **API Docs**: https://price-tracker-api.fly.dev/docs
- **GitHub Repo**: https://github.com/TU_USUARIO/price-tracker

## Comandos Útiles de Fly.io

```bash
fly status                  # Ver estado de la app
fly logs                    # Ver logs en tiempo real
fly ssh console            # Acceder al contenedor
fly scale count 1          # Escalar a 1 máquina
fly secrets list           # Ver variables configuradas
fly dashboard              # Abrir dashboard en navegador
```

## Mantenimiento

### Actualizar la aplicación

Cada vez que hagas cambios y los subas a GitHub:

```bash
git add .
git commit -m "Descripción de los cambios"
git push
```

Fly.io y Vercel desplegarán automáticamente los cambios.

Para redesplegar manualmente en Fly.io:
```bash
fly deploy
```

### Monitorear

- **Fly.io**: `fly logs` o dashboard en https://fly.io/dashboard
- **Vercel**: Dashboard con analytics y logs
- **Supabase**: Dashboard para ver la base de datos

## Costos

- **Fly.io**: Gratis (3 máquinas pequeñas, 256MB RAM, NO se duerme)
- **Vercel**: Gratis para proyectos personales
- **Supabase**: 500 MB gratis

## Ventajas de Fly.io

1. **NO se duerme**: Respuesta instantánea siempre
2. **Más rápido**: Contenedores optimizados
3. **Profesional**: Usas Docker (estándar de industria)
4. **Escalable**: Fácil escalar cuando crezca tu app

## Solución de Problemas

### Error: "Database connection failed"
- Verifica secrets: `fly secrets list`
- Asegúrate de que Supabase esté funcionando
- Revisa logs: `fly logs`

### Error: "CORS"
- Verifica que `ALLOWED_ORIGINS` incluya la URL de Vercel
- Actualiza con: `fly secrets set ALLOWED_ORIGINS="..."`

### Error: "Build failed"
- Asegúrate de que `Dockerfile` esté en la raíz
- Verifica que `requirements-production.txt` exista
- Revisa que no haya errores de sintaxis en el código

### App no responde
- Verifica status: `fly status`
- Revisa logs: `fly logs`
- Reinicia: `fly apps restart price-tracker-api`

## Siguiente Nivel

Una vez funcionando, considera:

1. Configurar un dominio personalizado
2. Añadir monitoreo con Sentry
3. Configurar GitHub Actions para CI/CD
4. Añadir tests automatizados

---

Desarrollado por **HellSpawn**

¡Tu aplicación ahora está en producción y lista para el mundo!
