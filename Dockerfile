# syntax=docker/dockerfile:1
FROM python:3.12.5-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    DJANGO_SETTINGS_MODULE=indstaal.settings \
    # make sure Django treats this as prod
    DJANGO_COLLECTSTATIC=1

WORKDIR /app

# System runtime deps only (no compilers). Use psycopg2-binary in requirements if possible.
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps first for better layer caching
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Collect static files to STATIC_ROOT (see settings below)
# RUN python manage.py collectstatic --noinput

EXPOSE 8080

# Preload app so WhiteNoise can find static manifest; tune workers as needed
CMD ["gunicorn", "indstaal.wsgi:application", \
    "--bind", "0.0.0.0:8080", \
    "--workers", "3", \
    "--timeout", "120", \
    "--preload"]
