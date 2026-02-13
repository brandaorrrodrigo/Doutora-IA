FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (including WeasyPrint requirements)
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    libpq-dev \
    fonts-liberation \
    libgobject-2.0-0 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libcairo2 \
    libffi-dev \
    shared-mime-info \
    libgdk-pixbuf-2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip to avoid segfault during dependency resolution
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Install in batches to avoid Docker Desktop WSL2 segfault during dependency resolution
# Batch 1: Core web framework
RUN pip install --no-cache-dir fastapi==0.109.0 "uvicorn[standard]==0.27.0" python-multipart==0.0.9

# Batch 2: Database + cache
RUN pip install --no-cache-dir sqlalchemy==2.0.25 psycopg2-binary==2.9.9 alembic==1.13.1 qdrant-client==1.7.3 redis==5.0.1

# Batch 3: Auth
RUN pip install --no-cache-dir "python-jose[cryptography]==3.3.0" "passlib[bcrypt]==1.7.4" bcrypt==4.1.2

# Batch 4: AI/ML - PyTorch CPU-only + OpenAI client
RUN pip install --no-cache-dir torch==2.5.1+cpu --extra-index-url https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir openai==1.7.2 httpx==0.26.0

# Batch 5a: Heavy scientific deps first
RUN pip install --no-cache-dir scipy scikit-learn Pillow

# Batch 5b: Transformers
RUN pip install --no-cache-dir "transformers>=4.38.0,<5.0.0"

# Batch 5c: Sentence-Transformers
RUN pip install --no-cache-dir "sentence-transformers>=2.6.0,<4.0.0"

# Batch 6: PDF/DOCX generation
RUN pip install --no-cache-dir weasyprint==60.2 reportlab==4.1.0 PyPDF2==3.0.1 "python-docx>=1.1.1" docxtpl==0.17.0

# Batch 7: Utils
RUN pip install --no-cache-dir jinja2==3.1.3 python-dotenv==1.0.0 pydantic==2.5.3 pydantic-settings==2.1.0 email-validator

# Batch 8: Payment providers
RUN pip install --no-cache-dir stripe mercadopago

# Copy application code
COPY . .

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8080}/health || exit 1

# Run the application (use PORT env var from Railway)
CMD ["sh", "-c", "python -m uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}"]
