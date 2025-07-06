from datetime import date
from psycopg2.extras import RealDictCursor
from .schema import VeiculoCriacao, VeiculoAtualizacao

def _construir_query_update(
    nome_tabela, dados, coluna_condicao, valor_condicao
):
    dados_update = dados.model_dump(
        exclude_unset=True, exclude={coluna_condicao}
    )
    if not dados_update:
        return None, []
    clausulas_set = [f"{chave} = %s" for chave in dados_update.keys()]
    query = (
        f"UPDATE {nome_tabela} SET {', '.join(clausulas_set)} "
        f"WHERE {coluna_condicao} = %s RETURNING *"
    )
    parametros = list(dados_update.values()) + [valor_condicao]
    return query, parametros

def criar_veiculo(conexao_banco, veiculo: VeiculoCriacao):
    with conexao_banco.cursor(cursor_factory=RealDictCursor) as cursor:
        query = """
            INSERT INTO veiculo
                (placa, modelo, marca, ano, valor_diaria)
            VALUES (%s, %s, %s, %s, %s) RETURNING *;
        """
        cursor.execute(
            query,
            (
                veiculo.placa, veiculo.modelo, veiculo.marca,
                veiculo.ano, veiculo.valor_diaria
            )
        )
        novo_veiculo = cursor.fetchone()
        conexao_banco.commit()
        return novo_veiculo

def obter_veiculos(conexao_banco):
    with conexao_banco.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute("SELECT * FROM veiculo ORDER BY veiculo_id;")
        return cursor.fetchall()

def obter_veiculo_por_id(conexao_banco, veiculo_id: int):
    with conexao_banco.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute(
            "SELECT * FROM veiculo WHERE veiculo_id = %s;", (veiculo_id,)
        )
        return cursor.fetchone()

def atualizar_veiculo(
    conexao_banco, veiculo_id: int, dados_veiculo: VeiculoAtualizacao
):
    query, parametros = _construir_query_update(
        "veiculo", dados_veiculo, "veiculo_id", veiculo_id
    )
    if not query:
        return obter_veiculo_por_id(conexao_banco, veiculo_id)
    with conexao_banco.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute(query, parametros)
        veiculo_atualizado = cursor.fetchone()
        if not veiculo_atualizado:
            return None
        conexao_banco.commit()
    return obter_veiculo_por_id(conexao_banco, veiculo_id)

def deletar_veiculo(conexao_banco, veiculo_id: int):
    with conexao_banco.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute(
            "DELETE FROM veiculo WHERE veiculo_id = %s RETURNING *;",
            (veiculo_id,)
        )
        veiculo_deletado = cursor.fetchone()
        conexao_banco.commit()
        return veiculo_deletado

def obter_veiculos_disponiveis(conexao_banco, data_inicio: date, data_fim: date):
    with conexao_banco.cursor(cursor_factory=RealDictCursor) as cursor:
        query_reservados = """
            SELECT DISTINCT veiculo_id FROM reserva
            WHERE (data_inicio, data_fim) OVERLAPS (%s, %s)
        """
        cursor.execute(query_reservados, (data_inicio, data_fim))
        veiculos_reservados = cursor.fetchall()
        ids_reservados = [item['veiculo_id'] for item in veiculos_reservados]

        if ids_reservados:
            query_disponiveis = (
                "SELECT * FROM veiculo WHERE veiculo_id NOT IN %s "
                "ORDER BY veiculo_id"
            )
            cursor.execute(query_disponiveis, (tuple(ids_reservados),))
        else:
            query_disponiveis = "SELECT * FROM veiculo ORDER BY veiculo_id"
            cursor.execute(query_disponiveis)

        return cursor.fetchall()