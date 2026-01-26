# -*- coding: utf-8 -*-
# Dockerfile - Doutora IA API
# Usa código da pasta api/ com autenticação JWT

FROM python:3.11-slim as builder

LABEL maintainer="Doutora IA <contato@doutoraai.com>"
LABEL description="API Jurídica com Autenticação"
LABEL version="2.0.0-auth"

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Instala dependências de build
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copia requirements da API e instala
COPY ../../api/requirements.txt .
RUN pip install --user --no-warn-script-location -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH=/root/.local/bin:$PATH \
    PORT=8080

# Instala dependências runtime (incluindo WeasyPrint)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    fonts-liberation \
    libgobject-2.0-0 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libcairo2 \
    libffi-dev \
    shared-mime-info \
    libgdk-pixbuf-2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copia dependências Python
COPY --from=builder /root/.local /root/.local

# Copia código da API
COPY ../../api/ .

# Cria diretórios
RUN mkdir -p /app/uploads /app/logs

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

EXPOSE ${PORT}

# Inicia API
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT}"]
