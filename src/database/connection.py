import os
import psycopg2
from dotenv import load_dotenv

# Carrega as variáveis de ambiente de um arquivo .env (útil para desenvolvimento local)
load_dotenv()

def obter_conexao_real_banco():
    """
    Obtém a conexão com o banco de dados usando a variável de ambiente DATABASE_URL.
    """
    db_url = os.environ.get("DATABASE_URL")
    
    if not db_url:
        raise ValueError("A variável de ambiente DATABASE_URL não foi definida.")
        
    conexao = psycopg2.connect(db_url)
    return conexao

def obter_conexao_banco():
    """
    Um gerador de dependência para o FastAPI.
    Ele cria uma conexão, a entrega (yield) para a rota, e garante
    que ela seja fechada ao final, mesmo que ocorra um erro.
    """
    conexao = None
    try:
        conexao = obter_conexao_real_banco()
        yield conexao
    finally:
        if conexao:
            conexao.close()
