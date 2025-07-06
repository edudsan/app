# Em database/init_db.py
import os
import psycopg2
from psycopg2 import sql

def initialize_database():
    """
    Verifica se o banco de dados precisa ser inicializado.
    Se uma tabela chave (ex: 'cliente') não existir, executa os scripts SQL
    para criar o schema e popular os dados iniciais.
    """
    # Pega a URL de conexão do banco a partir das variáveis de ambiente.
    # Esta é a forma como o Render e outras plataformas fornecem as credenciais.
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        print("ERRO: Variável de ambiente DATABASE_URL não definida.")
        return

    # Define o nome de uma tabela principal para verificar se o DB já foi iniciado
    table_to_check = 'cliente'
    
    conn = None
    try:
        # Conecta ao banco de dados
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()

        # Query para verificar se a tabela 'cliente' já existe
        cur.execute(sql.SQL("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = %s
            );
        """), [table_to_check])

        table_exists = cur.fetchone()[0]

        # Se a tabela não existe, o banco precisa ser inicializado
        if not table_exists:
            print("Banco de dados não inicializado. Executando scripts SQL...")

            # Constrói o caminho absoluto para os arquivos .sql
            # Isso garante que funcione independentemente de onde o script é chamado
            base_dir = os.path.dirname(os.path.abspath(__file__))
            schema_path = os.path.join(base_dir, 'init', '01_schema.sql')
            data_path = os.path.join(base_dir, 'init', '02_data.sql')

            # Executa o script de schema
            print(f"Executando {schema_path}...")
            with open(schema_path, 'r', encoding='utf-8') as f:
                cur.execute(f.read())

            # Executa o script de dados
            print(f"Executando {data_path}...")
            with open(data_path, 'r', encoding='utf-8') as f:
                cur.execute(f.read())
            
            # Confirma as transações
            conn.commit()
            print("Banco de dados inicializado com sucesso!")
        else:
            print("Banco de dados já está inicializado. Nenhuma ação necessária.")

        cur.close()

    except psycopg2.Error as e:
        print(f"Erro na inicialização do banco de dados: {e}")
    finally:
        if conn is not None:
            conn.close()

if __name__ == '__main__':
    # Permite executar este script diretamente para testes, se necessário
    # Você precisaria definir a DATABASE_URL no seu ambiente local
    print("Iniciando verificação manual do banco de dados...")
    initialize_database()