#!/bin/sh
# wait-for-db.sh

set -e

# O comando a ser executado após o banco estar pronto é passado como argumento para este script
cmd="$@"

# Loop até que o pg_isready retorne 0 (sucesso)
until pg_isready -h "db" -p "5432" -U "${POSTGRES_USER}"; do
  >&2 echo "Postgres ainda não está disponível - aguardando..."
  sleep 1
done

>&2 echo "Postgres está no ar - executando o comando"
# Executa o comando original (ex: pytest ou uvicorn)
exec $cmd