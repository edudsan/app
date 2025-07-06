from psycopg2.extras import RealDictCursor
from .schema import (
    PessoaFisicaCriacao, PessoaJuridicaCriacao, PessoaAtualizacao
)

def obter_clientes(conexao_banco):
    with conexao_banco.cursor(cursor_factory=RealDictCursor) as cursor:
        query = """
            SELECT p.*, row_to_json(e.*) as endereco FROM pessoa p
            LEFT JOIN endereco e ON p.endereco_id = e.endereco_id
            ORDER BY p.pessoa_id
        """
        cursor.execute(query)
        return cursor.fetchall()

def obter_cliente_por_id(conexao_banco, pessoa_id: int):
    with conexao_banco.cursor(cursor_factory=RealDictCursor) as cursor:
        query = """
            SELECT p.*, row_to_json(e.*) as endereco FROM pessoa p
            LEFT JOIN endereco e ON p.endereco_id = e.endereco_id
            WHERE p.pessoa_id = %s
        """
        cursor.execute(query, (pessoa_id,))
        return cursor.fetchone()

def criar_cliente_pf(conexao_banco, cliente: PessoaFisicaCriacao):
    with conexao_banco.cursor(cursor_factory=RealDictCursor) as cursor:
        query_endereco = """
            INSERT INTO endereco (rua, bairro, cidade, estado, numero)
            VALUES (%s, %s, %s, %s, %s) RETURNING endereco_id;
        """
        cursor.execute(
            query_endereco,
            (
                cliente.endereco.rua, cliente.endereco.bairro,
                cliente.endereco.cidade, cliente.endereco.estado,
                cliente.endereco.numero
            )
        )
        endereco_id = cursor.fetchone()['endereco_id']

        query_pessoa = """
            INSERT INTO pessoa
                (nome, email, telefone, tipo_pessoa, cpf, estado_civil,
                 endereco_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING pessoa_id;
        """
        cursor.execute(
            query_pessoa,
            (
                cliente.nome, cliente.email, cliente.telefone,
                cliente.tipo_pessoa, cliente.cpf, cliente.estado_civil,
                endereco_id
            )
        )
        pessoa_id = cursor.fetchone()['pessoa_id']
        conexao_banco.commit()
    return obter_cliente_por_id(conexao_banco, pessoa_id)

def criar_cliente_pj(conexao_banco, cliente: PessoaJuridicaCriacao):
    with conexao_banco.cursor(cursor_factory=RealDictCursor) as cursor:
        query_endereco = """
            INSERT INTO endereco (rua, bairro, cidade, estado, numero)
            VALUES (%s, %s, %s, %s, %s) RETURNING endereco_id;
        """
        cursor.execute(
            query_endereco,
            (
                cliente.endereco.rua, cliente.endereco.bairro,
                cliente.endereco.cidade, cliente.endereco.estado,
                cliente.endereco.numero
            )
        )
        endereco_id = cursor.fetchone()['endereco_id']

        query_pessoa = """
            INSERT INTO pessoa
                (nome, email, telefone, tipo_pessoa, cnpj, endereco_id)
            VALUES (%s, %s, %s, %s, %s, %s) RETURNING pessoa_id;
        """
        cursor.execute(
            query_pessoa,
            (
                cliente.nome, cliente.email, cliente.telefone,
                cliente.tipo_pessoa, cliente.cnpj, endereco_id
            )
        )
        pessoa_id = cursor.fetchone()['pessoa_id']
        conexao_banco.commit()
    return obter_cliente_por_id(conexao_banco, pessoa_id)

def atualizar_cliente(
    conexao_banco, pessoa_id: int, dados_cliente: PessoaAtualizacao
):
    with conexao_banco.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute(
            "SELECT endereco_id FROM pessoa WHERE pessoa_id = %s", (pessoa_id,)
        )
        resultado = cursor.fetchone()
        if not resultado:
            return None
        endereco_id = resultado['endereco_id']

        dados_pessoa = dados_cliente.model_dump(
            exclude_unset=True, exclude={'endereco'}
        )
        if dados_pessoa:
            clausulas = [f"{chave} = %s" for chave in dados_pessoa.keys()]
            query = f"UPDATE pessoa SET {', '.join(clausulas)} WHERE pessoa_id = %s"
            params = list(dados_pessoa.values()) + [pessoa_id]
            cursor.execute(query, params)

        if getattr(dados_cliente, 'endereco', None):
            dados_end = dados_cliente.endereco.model_dump(exclude_unset=True)
            if dados_end:
                clausulas = [f"{chave} = %s" for chave in dados_end.keys()]
                query_end = (
                    f"UPDATE endereco SET {', '.join(clausulas)} "
                    f"WHERE endereco_id = %s"
                )
                params_end = list(dados_end.values()) + [endereco_id]
                cursor.execute(query_end, params_end)

        conexao_banco.commit()
    return obter_cliente_por_id(conexao_banco, pessoa_id)

def deletar_cliente(conexao_banco, pessoa_id: int):
    with conexao_banco.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute(
            "SELECT endereco_id FROM pessoa WHERE pessoa_id = %s", (pessoa_id,)
        )
        resultado = cursor.fetchone()
        if not resultado:
            return None

        endereco_id = resultado['endereco_id']

        cursor.execute(
            "DELETE FROM pessoa WHERE pessoa_id = %s RETURNING *;", (pessoa_id,)
        )
        pessoa_deletada = cursor.fetchone()

        if pessoa_deletada and endereco_id:
            cursor.execute(
                "DELETE FROM endereco WHERE endereco_id = %s;", (endereco_id,)
            )

        conexao_banco.commit()
        return pessoa_deletada