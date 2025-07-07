import os
from contextlib import contextmanager
import psycopg2
from dotenv import load_dotenv

# Carrega as variáveis de ambiente de um arquivo .env (útil para desenvolvimento local)
load_dotenv()

def obter_conexao_real_banco():
    """
    Obtém a conexão com o banco de dados usando a variável de ambiente DATABASE_URL.
    Esta é a forma correta para funcionar tanto no Render quanto localmente.
    """
    # Pega a URL de conexão completa da variável de ambiente.
    db_url = os.environ.get("DATABASE_URL")
    
    if not db_url:
        raise ValueError("A variável de ambiente DATABASE_URL não foi definida.")
        
    # Conecta ao banco de dados usando a URL.
    conexao = psycopg2.connect(db_url)
    return conexao

@contextmanager
def obter_conexao_banco():
    """
    Um gerenciador de contexto para garantir que a conexão com o banco
    seja sempre fechada corretamente.
    """
    conexao = None
    try:
        conexao = obter_conexao_real_banco()
        yield conexao
    finally:
        if conexao:
            conexao.close()

