# Dockerfile (Versão Final Corrigida)

FROM python:3.11-slim

# NOVO: Instala o dos2unix junto com o cliente postgresql
# O dos2unix converte arquivos de texto do formato Windows para o formato Unix.
RUN apt-get update && apt-get install -y postgresql-client dos2unix && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copia o script para dentro do container
COPY ./wait-for-db.sh /app/wait-for-db.sh

# --- INÍCIO DA CORREÇÃO ROBUSTA ---
# Passo 1 (NOVO): Converte o script de line endings do Windows (CRLF) para Unix (LF).
# Isso previne erros de execução em ambientes Linux.
RUN dos2unix /app/wait-for-db.sh

# Passo 2: DÁ A PERMISSÃO DE EXECUÇÃO
RUN chmod +x /app/wait-for-db.sh
# --- FIM DA CORREÇÃO ROBUSTA ---

# Instala as dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o resto do código da aplicação
COPY . .

# O comando de inicialização
CMD ./wait-for-db.sh uvicorn src.main:app --host 0.0.0.0 --port $PORT
