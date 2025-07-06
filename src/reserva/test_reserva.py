# src/reserva/test_reserva.py
import uuid
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def unique_suffix():
    return uuid.uuid4().hex[:6]

class TestReservas:
    def test_ciclo_de_vida_reserva(self):
        """Testa o ciclo de vida completo de uma reserva."""
        suffix = unique_suffix()
        email, cpf = f"reserva.{suffix}@teste.com", f"777.777.777-{suffix[:2]}"
        placa = f"RES-{suffix[:4]}"

        cliente_id, veiculo_id, reserva_id = None, None, None
        try:
            # 1. Criar dependências
            cliente_res = client.post("/clientes/pf", json={
                "nome": "Cliente para Reserva", "email": email, "cpf": cpf,
                "endereco": {"rua": "Rua R", "cidade": "C", "estado": "E"}
            })
            assert cliente_res.status_code == 201, f"Falha ao criar cliente: {cliente_res.text}"
            cliente_id = cliente_res.json()["pessoa_id"]

            veiculo_res = client.post("/veiculos", json={
                "placa": placa, "modelo": "Carro de Reserva", "valor_diaria": 200.00
            })
            assert veiculo_res.status_code == 201, f"Falha ao criar veículo: {veiculo_res.text}"
            veiculo_id = veiculo_res.json()["veiculo_id"]

            # 2. Criar Reserva
            response = client.post("/reservas", json={
                "cliente_id": cliente_id, "veiculo_id": veiculo_id,
                "data_inicio": "2025-10-10", "data_fim": "2025-10-15", "tipo_reserva": "Normal"
            })
            assert response.status_code == 201
            reserva_id = response.json()["reserva_id"]
            assert response.json()["diarias"] == 5

            # 3. Editar Reserva
            response_edicao = client.put(f"/reservas/{reserva_id}", 
            json={"data_fim": "2025-10-17"})
            assert response_edicao.status_code == 200
            assert response_edicao.json()["diarias"] == 7

            # 4. Testar conflito
            reserva_conflitante = {
                "cliente_id": cliente_id, "veiculo_id": veiculo_id,
                "data_inicio": "2025-10-16", "data_fim": "2025-10-18", "tipo_reserva": "Normal"
            }
            response_conflito = client.post("/reservas", json=reserva_conflitante)
            assert response_conflito.status_code == 409
        finally:
            # 5. Limpeza (na ordem inversa da criação)
            if reserva_id: client.delete(f"/reservas/{reserva_id}")
            if cliente_id: client.delete(f"/clientes/{cliente_id}")
            if veiculo_id: client.delete(f"/veiculos/{veiculo_id}")

    def test_relatorio_faturamento(self):
        """Testa o relatório de faturamento."""
        suffix = unique_suffix()
        email, cpf = f"report.{suffix}@teste.com", f"999.999.999-{suffix[:2]}"
        placa = f"REP-{suffix[:4]}"

        c1_id, v1_id = None, None
        reservas_criadas_ids = []
        try:
            # 1. Criar dependências
            c1_res = client.post("/clientes/pf", json={"nome": "Report Cli 1",
            "email": email, "cpf": cpf, "endereco": {"rua":"r","cidade":"c","estado":"e"}})
            assert c1_res.status_code == 201
            c1_id = c1_res.json()["pessoa_id"]

            v1_res = client.post("/veiculos", json={"placa": placa, 
            "modelo": "Relatorio Car 1", "valor_diaria": 100})
            assert v1_res.status_code == 201
            v1_id = v1_res.json()["veiculo_id"]
            
            # 2. Criar reservas e guardar seus IDs
            res1 = client.post("/reservas", json={"cliente_id":c1_id, 
            "veiculo_id":v1_id, "data_inicio":"2025-08-01",
            "data_fim":"2025-08-03", "tipo_reserva":"R1"})
            reservas_criadas_ids.append(res1.json()["reserva_id"])

            res2 = client.post("/reservas", json={"cliente_id":c1_id,
            "veiculo_id":v1_id, "data_inicio":"2025-08-10", 
            "data_fim":"2025-08-15", "tipo_reserva":"R2"})
            reservas_criadas_ids.append(res2.json()["reserva_id"])

            res3 = client.post("/reservas", json={"cliente_id":c1_id,
            "veiculo_id":v1_id, "data_inicio":"2025-09-01",
            "data_fim":"2025-09-05", "tipo_reserva":"R3"})
            reservas_criadas_ids.append(res3.json()["reserva_id"])


            # 3. Gerar e verificar o relatório
            response = client.get("/reservas/relatorio/faturamento/?data_inicio=2025-08-01&data_fim=2025-08-31")
            assert response.status_code == 200
            report = response.json()
            
            assert report["total_reservas"] == 2
            assert report["faturamento_total"] == 700.00
        finally:
            # Limpeza completa e na ordem correta
            for r_id in reservas_criadas_ids:
                client.delete(f"/reservas/{r_id}")
            if c1_id: client.delete(f"/clientes/{c1_id}")
            if v1_id: client.delete(f"/veiculos/{v1_id}")