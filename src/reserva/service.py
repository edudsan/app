from datetime import date
from psycopg2.extras import RealDictCursor
from .schema import ReservaCriacao, ReservaAtualizacao

def obter_reserva_por_id(conexao_banco, reserva_id: int):
    with conexao_banco.cursor(cursor_factory=RealDictCursor) as cursor:
        query = """
            SELECT
                r.*,
                row_to_json(v.*) AS veiculo,
                (
                    SELECT json_build_object(
                        'pessoa_id', p.pessoa_id, 'nome', p.nome,
                        'email', p.email, 'telefone', p.telefone,
                        'tipo_pessoa', p.tipo_pessoa, 'cpf', p.cpf,
                        'estado_civil', p.estado_civil, 'cnpj', p.cnpj,
                        'endereco', row_to_json(e.*)
                    )
                    FROM pessoa p
                    JOIN endereco e ON p.endereco_id = e.endereco_id
                    WHERE p.pessoa_id = r.cliente_id
                ) AS cliente
            FROM reserva r
            JOIN veiculo v ON r.veiculo_id = v.veiculo_id
            WHERE r.reserva_id = %s;
        """
        cursor.execute(query, (reserva_id,))
        return cursor.fetchone()

def criar_reserva(conexao_banco, reserva: ReservaCriacao):
    with conexao_banco.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute(
            "SELECT valor_diaria FROM veiculo WHERE veiculo_id = %s;",
            (reserva.veiculo_id,)
        )
        veiculo = cursor.fetchone()
        if not veiculo:
            raise ValueError("Veículo não encontrado.")

        cursor.execute(
            "SELECT pessoa_id FROM pessoa WHERE pessoa_id = %s;",
            (reserva.cliente_id,)
        )
        if not cursor.fetchone():
            raise ValueError("Cliente não encontrado.")

        query_conflito = """
            SELECT reserva_id FROM reserva
            WHERE veiculo_id = %s AND (data_inicio, data_fim) OVERLAPS (%s, %s)
        """
        cursor.execute(
            query_conflito,
            (reserva.veiculo_id, reserva.data_inicio, reserva.data_fim)
        )
        if cursor.fetchone():
            raise ValueError("O veículo já está reservado para este período.")

        diarias = (reserva.data_fim - reserva.data_inicio).days
        if diarias <= 0:
            raise ValueError("Data de fim deve ser posterior à data de início.")
        valor_total = diarias * veiculo['valor_diaria']

        query_insert = """
            INSERT INTO reserva
                (data_inicio, data_fim, diarias, valor_total, tipo_reserva,
                 cliente_id, veiculo_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING reserva_id;
        """
        cursor.execute(
            query_insert,
            (
                reserva.data_inicio, reserva.data_fim, diarias, valor_total,
                reserva.tipo_reserva, reserva.cliente_id, reserva.veiculo_id
            )
        )
        reserva_id = cursor.fetchone()['reserva_id']
        conexao_banco.commit()

        return obter_reserva_por_id(conexao_banco, reserva_id)

def atualizar_reserva(
    conexao_banco, reserva_id: int, dados_reserva: ReservaAtualizacao
):
    with conexao_banco.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute(
            "SELECT * FROM reserva WHERE reserva_id = %s;", (reserva_id,)
        )
        reserva_existente = cursor.fetchone()
        if not reserva_existente:
            raise ValueError("Reserva não encontrada.")

        dados_atualizados = dados_reserva.model_dump(exclude_unset=True)
        data_inicio = dados_atualizados.get(
            'data_inicio', reserva_existente['data_inicio']
        )
        data_fim = dados_atualizados.get(
            'data_fim', reserva_existente['data_fim']
        )
        veiculo_id = reserva_existente['veiculo_id']

        if data_fim <= data_inicio:
            raise ValueError("A data de fim deve ser posterior à data de início.")

        query_conflito = """
            SELECT reserva_id FROM reserva
            WHERE veiculo_id = %s AND reserva_id != %s
            AND (data_inicio, data_fim) OVERLAPS (%s, %s)
        """
        cursor.execute(
            query_conflito, (veiculo_id, reserva_id, data_inicio, data_fim)
        )
        if cursor.fetchone():
            msg = "O veículo já está reservado para o novo período solicitado."
            raise ValueError(msg)

        cursor.execute(
            "SELECT valor_diaria FROM veiculo WHERE veiculo_id = %s;", (veiculo_id,)
        )
        valor_diaria = cursor.fetchone()['valor_diaria']

        diarias = (data_fim - data_inicio).days
        valor_total = diarias * valor_diaria
        dados_atualizados['diarias'] = diarias
        dados_atualizados['valor_total'] = valor_total

        clausulas = [f"{chave} = %s" for chave in dados_atualizados.keys()]
        query = f"UPDATE reserva SET {', '.join(clausulas)} WHERE reserva_id = %s"
        params = list(dados_atualizados.values()) + [reserva_id]

        cursor.execute(query, params)
        conexao_banco.commit()

    return obter_reserva_por_id(conexao_banco, reserva_id)

def obter_reservas(conexao_banco):
    with conexao_banco.cursor(cursor_factory=RealDictCursor) as cursor:
        query = """
            SELECT r.*,
                   row_to_json(v.*) AS veiculo,
                   (SELECT json_build_object(
                        'pessoa_id', p.pessoa_id, 'nome', p.nome,
                        'email', p.email, 'telefone', p.telefone,
                        'tipo_pessoa', p.tipo_pessoa, 'cpf', p.cpf,
                        'estado_civil', p.estado_civil, 'cnpj', p.cnpj,
                        'endereco', row_to_json(e.*)
                    )
                    FROM pessoa p JOIN endereco e ON p.endereco_id = e.endereco_id
                    WHERE p.pessoa_id = r.cliente_id
                   ) AS cliente
            FROM reserva r JOIN veiculo v ON r.veiculo_id = v.veiculo_id
            ORDER BY r.reserva_id;
        """
        cursor.execute(query)
        return cursor.fetchall()

def gerar_relatorio_faturamento(conexao_banco, data_inicio: date, data_fim: date):
    with conexao_banco.cursor(cursor_factory=RealDictCursor) as cursor:
        query = "SELECT * FROM reserva WHERE data_inicio BETWEEN %s AND %s"
        cursor.execute(query, (data_inicio, data_fim))
        ids_reservas = [r['reserva_id'] for r in cursor.fetchall()]

        if not ids_reservas:
            return {
                "periodo_inicio": data_inicio, "periodo_fim": data_fim,
                "total_reservas": 0, "faturamento_total": 0.0,
                "reservas_incluidas": []
            }

        reservas_completas = [
            obter_reserva_por_id(conexao_banco, r_id) for r_id in ids_reservas
        ]
        faturamento_total = sum(r['valor_total'] for r in reservas_completas)

        return {
            "periodo_inicio": data_inicio,
            "periodo_fim": data_fim,
            "total_reservas": len(reservas_completas),
            "faturamento_total": faturamento_total,
            "reservas_incluidas": reservas_completas
        }

def deletar_reserva(conexao_banco, reserva_id: int):
    with conexao_banco.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute(
            "DELETE FROM reserva WHERE reserva_id = %s RETURNING *;",
            (reserva_id,)
        )
        reserva_deletada = cursor.fetchone()
        conexao_banco.commit()
        return reserva_deletada