# Guía de Instalación de PostgreSQL

## Opción 1: Instalación Local (Recomendado para desarrollo)

### Descargar PostgreSQL
1. Ve a: https://www.postgresql.org/download/windows/
2. Descarga el instalador oficial
3. Ejecuta el instalador

### Durante la Instalación
- **Puerto**: Deja el puerto por defecto (5432)
- **Contraseña del superusuario (postgres)**: Usa `postgres` (o la que prefieras)
- **Locale**: Deja el valor por defecto

### Después de Instalar
1. Abre pgAdmin 4 (se instala automáticamente)
2. Conéctate con la contraseña que estableciste
3. Crea una nueva base de datos:
   - Click derecho en "Databases" > "Create" > "Database"
   - Name: `price_tracker`
   - Owner: `postgres`
   - Click "Save"

### Actualizar archivo .env
```env
DATABASE_URL=postgresql://postgres:TU_CONTRASEÑA@localhost:5432/price_tracker
```

---

## Opción 2: PostgreSQL con Docker (Alternativa rápida)

Si tienes Docker instalado:

```bash
docker run --name postgres-price-tracker \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=price_tracker \
  -p 5432:5432 \
  -d postgres:15
```

URL de conexión:
```
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/price_tracker
```

---

## Opción 3: Base de Datos en la Nube (Gratis)

### Supabase (Recomendado)
1. Ve a: https://supabase.com/
2. Crea una cuenta gratuita
3. Crea un nuevo proyecto
4. Ve a Settings > Database
5. Copia la "Connection String" (URI)
6. Pégala en tu archivo .env

### Railway (Alternativa)
1. Ve a: https://railway.app/
2. Crea una cuenta con GitHub
3. "New Project" > "Provision PostgreSQL"
4. Copia la "Postgres Connection URL"
5. Pégala en tu archivo .env

---

## Verificar Instalación

Después de instalar PostgreSQL, ejecuta:

```cmd
psql -U postgres -d price_tracker
```

Si todo funciona, verás el prompt de PostgreSQL.

---

## Inicializar Base de Datos

Una vez configurado PostgreSQL, ejecuta:

```cmd
cd c:\Users\leoac\Documents\School\Coding\ProyectosPersonales\RastreadorPrecios
.venv\Scripts\python.exe -m backend.app.database
```

Esto creará todas las tablas automáticamente.

---

## Troubleshooting

### Error: "Could not connect to server"
- Verifica que PostgreSQL esté corriendo
- En Windows: Services > PostgreSQL > Start

### Error: "password authentication failed"
- Verifica la contraseña en el archivo .env
- Prueba con: `postgres` como contraseña

### Error: "database does not exist"
- Crea la base de datos manualmente en pgAdmin
- O usa: `createdb -U postgres price_tracker`
