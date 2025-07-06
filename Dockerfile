# Dockerfile (Versão Corrigida para Produção)

FROM python:3.11-slim

# Instala o cliente do PostgreSQL para ter acesso ao comando 'pg_isready'
RUN apt-get update && apt-get install -y postgresql-client && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copia o script de espera e o torna executável
COPY ./wait-for-db.sh /app/wait-for-db.sh
RUN chmod +x /app/wait-for-db.sh

# Instala as dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o resto do código da aplicação
COPY . .

# O comando de inicialização.
# Nota: Usamos a "forma shell" (sem colchetes) para que a variável $PORT seja expandida.
# O Render irá substituir $PORT pelo número da porta correta.
CMD ./wait-for-db.sh uvicorn src.main:app --host 0.0.0.0 --port $PORT