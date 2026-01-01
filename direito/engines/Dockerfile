# -*- coding: utf-8 -*-
# Dockerfile - Doutora IA Engines API
# Multi-stage build para otimizar tamanho da imagem

# Stage 1: Builder
FROM python:3.11-slim as builder

# Metadata
LABEL maintainer="Doutora IA <contato@doutoraai.com>"
LABEL description="API de Automação Jurídica com 550 Engines"
LABEL version="2.0"

# Variáveis de ambiente para build
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Instala dependências do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Cria diretório de trabalho
WORKDIR /app

# Copia requirements e instala dependências Python
COPY requirements_api.txt .
RUN pip install --user --no-warn-script-location -r requirements_api.txt

# Stage 2: Runtime
FROM python:3.11-slim

# Variáveis de ambiente
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH=/root/.local/bin:$PATH \
    PORT=8000 \
    WORKERS=4 \
    TIMEOUT=120 \
    LOG_LEVEL=info

# Instala apenas dependências runtime mínimas
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Cria usuário não-root para segurança
RUN useradd -m -u 1000 -s /bin/bash appuser

# Cria diretório de trabalho
WORKDIR /app

# Copia dependências Python do builder
COPY --from=builder /root/.local /root/.local

# Copia código da aplicação
COPY --chown=appuser:appuser . .

# Cria diretórios necessários
RUN mkdir -p /app/logs /app/tmp && \
    chown -R appuser:appuser /app

# Muda para usuário não-root
USER appuser

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# Expõe porta
EXPOSE ${PORT}

# Script de inicialização
CMD ["sh", "-c", "uvicorn api_assistente_publico:app --host 0.0.0.0 --port ${PORT} --workers ${WORKERS} --timeout-keep-alive ${TIMEOUT} --log-level ${LOG_LEVEL}"]
