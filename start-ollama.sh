#!/bin/bash

# ============================================
# STARTUP SCRIPT - Ollama + FastAPI
# ============================================

set -e

echo "🚀 Starting Doutora IA with Ollama..."

# Start Ollama in background
echo "📦 Starting Ollama server..."
ollama serve &
OLLAMA_PID=$!

# Wait for Ollama to be ready
echo "⏳ Waiting for Ollama to start..."
for i in {1..30}; do
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo "✅ Ollama is ready!"
        break
    fi
    echo "   Waiting... ($i/30)"
    sleep 2
done

# Pull a small, fast model
echo "📥 Pulling Ollama model..."
MODEL="${LLM_MODEL:-qwen2:0.5b}"

if ! ollama list | grep -q "$MODEL"; then
    echo "   Downloading $MODEL (this may take a few minutes on first run)..."
    ollama pull "$MODEL"
    echo "✅ Model downloaded!"
else
    echo "✅ Model already available!"
fi

# Run database migrations
echo "🔄 Running database migrations..."
if [ -f "alembic.ini" ]; then
    alembic upgrade head || echo "⚠️  Migrations failed or not needed"
fi

# Start FastAPI
echo "🚀 Starting FastAPI server..."
exec uvicorn main:app \
    --host 0.0.0.0 \
    --port ${PORT:-8000} \
    --workers ${WORKERS:-1}
