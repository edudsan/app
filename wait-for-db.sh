#!/bin/sh
# wait-for-db.sh (Versão Universal)
# Este script espera o banco de dados ficar disponível usando a variável de ambiente DATABASE_URL.

set -e

# Pega todos os argumentos passados para este script (o comando uvicorn)
cmd="$@"

# Verifica se a variável DATABASE_URL foi definida.
if [ -z "$DATABASE_URL" ]; then
  >&2 echo "Erro: A variável de ambiente DATABASE_URL não está definida."
  exit 1
fi

# Loop até que o banco de dados na DATABASE_URL esteja pronto.
# O comando 'pg_isready' pode receber a URL de conexão completa com a flag -d.
until pg_isready -d "$DATABASE_URL" -q; do
  >&2 echo "Postgres ainda não está disponível - aguardando..."
  sleep 1
done

>&2 echo "Postgres está no ar - executando o comando."
# Executa o comando original que foi passado como argumento (ex: uvicorn ...)
exec $cmd
