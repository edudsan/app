# Dockerfile (Versão Final Corrigida)

FROM python:3.11-slim

# Instala o cliente postgresql, necessário para o comando 'pg_isready'
RUN apt-get update && apt-get install -y postgresql-client && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Instala as dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o resto do código da aplicação
COPY . .

# O comando de inicialização agora inclui a lógica de espera diretamente.
# Isso evita qualquer problema de permissão de arquivo com scripts externos.
# Usamos a "forma shell" (sem colchetes) para que a variável $PORT seja expandida.
CMD while ! pg_isready -d "$DATABASE_URL" -q; do echo "Aguardando o banco de dados..."; sleep 1; done && uvicorn src.main:app --host 0.0.0.0 --port $PORT
