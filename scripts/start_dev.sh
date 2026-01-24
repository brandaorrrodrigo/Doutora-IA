#!/bin/bash
# Doutora IA - Script de Desenvolvimento Local
# Execute: ./scripts/start_dev.sh

set -e

echo "======================================"
echo "  DOUTORA IA - Ambiente de Desenvolvimento"
echo "======================================"

# Verificar Docker
echo -e "\nVerificando Docker..."
if ! docker info > /dev/null 2>&1; then
    echo "ERRO: Docker não está rodando!"
    echo "Por favor, inicie o Docker e tente novamente."
    exit 1
fi
echo "Docker OK!"

# Subir serviços básicos (PostgreSQL, Qdrant, Redis)
echo -e "\nSubindo serviços básicos (db, qdrant, redis)..."
docker-compose up -d db qdrant redis

# Aguardar PostgreSQL
echo -e "\nAguardando PostgreSQL ficar pronto..."
max_attempts=30
attempt=0
until docker exec doutora-db pg_isready -U postgres > /dev/null 2>&1 || [ $attempt -eq $max_attempts ]; do
    attempt=$((attempt + 1))
    sleep 1
done
if [ $attempt -eq $max_attempts ]; then
    echo "ERRO: PostgreSQL não iniciou a tempo"
    exit 1
fi
echo "PostgreSQL pronto!"

# Aguardar Qdrant
echo -e "\nAguardando Qdrant ficar pronto..."
attempt=0
until curl -s http://localhost:6333/health > /dev/null 2>&1 || [ $attempt -eq $max_attempts ]; do
    attempt=$((attempt + 1))
    sleep 1
done
echo "Qdrant pronto!"

# Ingerir dados de sample
echo -e "\nIngerindo dados de sample no Qdrant..."
python scripts/ingest_full_corpus.py --samples

echo -e "\n======================================"
echo "  Ambiente pronto!"
echo "======================================"
echo -e "\nPara iniciar a API:"
echo "  cd api"
echo "  python -m uvicorn main:app --reload --port 8080"
echo -e "\nAcesse:"
echo "  API:     http://localhost:8080"
echo "  Docs:    http://localhost:8080/docs"
echo "  Qdrant:  http://localhost:6333/dashboard"
