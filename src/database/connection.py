import os
import psycopg2
from dotenv import load_dotenv

def obter_conexao_real_banco():
    load_dotenv()

    conexao = psycopg2.connect(
        host="db",
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD")
    )
    return conexao

def obter_conexao_banco():
    conexao = None
    try:
        conexao = obter_conexao_real_banco()
        yield conexao
    finally:
        if conexao is not None:
            conexao.close()