# Migración a PostgreSQL - Guía Rápida

## Opción Recomendada: Supabase (Gratis, 5 minutos)

### Paso 1: Crear Cuenta en Supabase

1. Ve a: **https://supabase.com/**
2. Click en "Start your project"
3. Inicia sesión con GitHub
4. Acepta los permisos

### Paso 2: Crear Proyecto

1. Click en "New Project"
2. Configura:
   - **Name**: price-tracker (o el que prefieras)
   - **Database Password**: Elige una contraseña segura (GUÁRDALA!)
   - **Region**: Elige el más cercano (US East recomendado)
   - **Pricing Plan**: Free (suficiente para empezar)
3. Click "Create new project"
4. Espera 1-2 minutos mientras se crea

### Paso 3: Obtener Connection String

1. En el dashboard de tu proyecto, ve a:
   - **Settings** (ícono de engranaje abajo a la izquierda)
   - **Database**
   - Scroll hasta "Connection string"
2. Selecciona la pestaña **"URI"**
3. Copia el string que se ve así:
   ```
   postgresql://postgres:[YOUR-PASSWORD]@db.xxx.supabase.co:5432/postgres
   ```
4. **IMPORTANTE**: Reemplaza `[YOUR-PASSWORD]` con la contraseña que elegiste

### Paso 4: Actualizar .env

Abre el archivo `.env` en tu proyecto y actualiza la línea:

```env
# Cambiar de:
DATABASE_URL=sqlite:///./price_tracker.db

# A (con tu connection string):
DATABASE_URL=postgresql://postgres:tu_password@db.xxx.supabase.co:5432/postgres
```

### Paso 5: Reiniciar Backend

Detén el servidor backend (Ctrl+C) y vuelve a iniciarlo:

```cmd
.venv\Scripts\python.exe -m uvicorn backend.app.main:app --reload
```

¡Listo! Las tablas se crearán automáticamente en PostgreSQL.

---

## Alternativa: Railway (También Gratis)

### Paso 1: Crear Cuenta
1. Ve a: **https://railway.app/**
2. Inicia sesión con GitHub

### Paso 2: Nuevo Proyecto
1. Click "New Project"
2. Click "Provision PostgreSQL"
3. Espera 30 segundos

### Paso 3: Obtener Connection String
1. Click en el servicio PostgreSQL
2. Ve a "Connect"
3. Copia la "Postgres Connection URL"

### Paso 4: Actualizar .env
```env
DATABASE_URL=postgresql://postgres:password@containers-us-west-xxx.railway.app:7432/railway
```

### Paso 5: Reiniciar Backend
```cmd
.venv\Scripts\python.exe -m uvicorn backend.app.main:app --reload
```

---

## ¿Qué pasa con los datos de SQLite?

Los datos actuales en SQLite NO se migran automáticamente. Opciones:

1. **Empezar de cero** (más fácil):
   - Simplemente cambia a PostgreSQL
   - Crea nuevas cuentas y productos

2. **Migrar datos** (avanzado):
   - Requiere script de migración
   - Exportar de SQLite e importar a PostgreSQL
   - Te puedo ayudar con esto si lo necesitas

---

## Verificar Migración Exitosa

Después de reiniciar el backend, verifica:

1. El backend inicia sin errores
2. Los logs muestran: "Database initialized successfully"
3. Puedes crear una nueva cuenta en http://localhost:5173/register
4. Los productos se guardan correctamente

---

## Troubleshooting

### Error: "could not translate host name"
- Verifica que copiaste bien la connection string
- Asegúrate de reemplazar [YOUR-PASSWORD]

### Error: "password authentication failed"
- La contraseña en el URL está incorrecta
- Verifica que usaste la contraseña correcta de Supabase/Railway

### Error: "SSL required"
Añade `?sslmode=require` al final del DATABASE_URL:
```env
DATABASE_URL=postgresql://postgres:pass@host:5432/db?sslmode=require
```

---

## Siguiente Paso

Una vez que PostgreSQL esté funcionando, ¡tu app estará lista para producción!

Puedes desplegarla en:
- **Frontend**: Vercel, Netlify
- **Backend**: Railway, Render, Fly.io
- **Base de Datos**: Ya está en Supabase/Railway
