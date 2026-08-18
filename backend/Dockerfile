# ── Etapa 1: instalar dependencias ──
FROM python:3.12-slim AS builder

WORKDIR /build
RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ── Etapa 2: imagen final mínima ──
FROM python:3.12-slim

WORKDIR /app

# Copiar solo los paquetes instalados (sin pip ni compiladores)
COPY --from=builder /install /usr/local

# Copiar el código de la aplicación
COPY ./app ./app

# Usuario no-root por seguridad
RUN adduser --disabled-password --gecos "" appuser && \
    chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", \
     "--host", "0.0.0.0", \
     "--port", "8000", \
     "--workers", "2"]
