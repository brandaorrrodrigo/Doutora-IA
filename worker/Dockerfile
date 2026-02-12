FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies (torch CPU-only for embeddings)
RUN pip install --no-cache-dir -r requirements.txt || \
    (pip install --no-cache-dir torch==2.1.2 --index-url https://download.pytorch.org/whl/cpu && \
     pip install --no-cache-dir -r requirements.txt)

# Copy application code
COPY . .

# Run the worker
CMD ["python", "worker.py"]
