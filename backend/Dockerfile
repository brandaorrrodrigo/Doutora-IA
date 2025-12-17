FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

# Test if files exist
RUN ls -la /app/

CMD ["sh", "-c", "echo 'Starting server...' && uvicorn main:app --host 0.0.0.0 --port 8080"]
