# Dockerfile (Versão Final Corrigida)

FROM python:3.11-slim

RUN apt-get update && apt-get install -y postgresql-client && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Passo 1: Copia o script para dentro do container
COPY ./wait-for-db.sh /app/wait-for-db.sh

# Passo 2: DÁ A PERMISSÃO DE EXECUÇÃO - ESTA É A LINHA CRÍTICA!
RUN chmod +x /app/wait-for-db.sh

# Instala as dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o resto do código da aplicação
COPY . .

# O comando de inicialização
CMD ./wait-for-db.sh uvicorn src.main:app --host 0.0.0.0 --port $PORT
