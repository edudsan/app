# Dockerfile

FROM python:3.11-slim

# NOVO: Instala o cliente do PostgreSQL para ter acesso ao comando 'pg_isready'
RUN apt-get update && apt-get install -y postgresql-client && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY ./wait-for-db.sh /app/wait-for-db.sh
RUN chmod +x /app/wait-for-db.sh

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["./wait-for-db.sh", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]