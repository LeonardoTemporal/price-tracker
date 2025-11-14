# Usa Python 3.12 slim para menor tamaño
FROM python:3.12-slim

# Variables de entorno para Python
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Directorio de trabajo
WORKDIR /app

# Copia todo el código primero
COPY . .

# Instala dependencias
RUN pip install --no-cache-dir -r requirements-production.txt

# Expone el puerto que usará Fly.io
EXPOSE 8000

# Comando para iniciar la aplicación (usa PORT si está definido, sino 8000)
CMD uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT:-8000}
