# src/veiculo/test_veiculo.py
import uuid
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def unique_suffix():
    return uuid.uuid4().hex[:6]

class TestVeiculos:
    def test_ciclo_de_vida_veiculo(self):
        """Testa o ciclo de vida completo de um veículo."""
        placa = f"TEST-{unique_suffix()[:4]}"
        veiculo_id = None
        try:
            # 1. Criar
            novo_veiculo = {"placa": placa, "modelo": "Fusca",
            "valor_diaria": 100.00}
            response = client.post("/veiculos", json=novo_veiculo)
            assert response.status_code == 201
            data = response.json()
            veiculo_id = data["veiculo_id"]
            assert data["placa"] == placa

            # 2. Ler
            response = client.get(f"/veiculos/{veiculo_id}")
            assert response.status_code == 200

            # 3. Atualizar
            dados_atualizados = {"valor_diaria": 125.50}
            response = client.put(f"/veiculos/{veiculo_id}",
            json=dados_atualizados)
            assert response.status_code == 200
            assert response.json()["valor_diaria"] == 125.50
        finally:
            # 4. Limpeza
            if veiculo_id:
                client.delete(f"/veiculos/{veiculo_id}")

    def test_buscar_veiculos_disponiveis(self):
        """Testa a busca por veículos disponíveis em um período."""
        suffix = unique_suffix()
        placa1, placa2 = f"DISP-{suffix[:3]}1", f"DISP-{suffix[:3]}2"
        email, cpf = f"disp.{suffix}@teste.com", f"888.888.888-{suffix[:2]}"
        
        v1_id, v2_id, cliente_id, reserva_id = None, None, None, None
        try:
            # 1. Criar um cenário: dois veículos e uma reserva
            v1_res = client.post("/veiculos",
            json={"placa": placa1, "modelo": "Carro A", "valor_diaria": 100})
            assert v1_res.status_code == 201
            v1_id = v1_res.json()["veiculo_id"]
            
            v2_res = client.post("/veiculos",
            json={"placa": placa2, "modelo": "Carro B", "valor_diaria": 100})
            assert v2_res.status_code == 201
            v2_id = v2_res.json()["veiculo_id"]

            cliente_res = client.post("/clientes/pf", json={
                "nome": "Cliente Disponibilidade", "email": email, "cpf": cpf,
                "endereco": {"rua": "Rua D", "cidade": "C", "estado": "E"}
            })
            assert cliente_res.status_code == 201
            cliente_id = cliente_res.json()["pessoa_id"]

            reserva_res = client.post("/reservas", json={
                "cliente_id": cliente_id, "veiculo_id": v1_id,
                "data_inicio": "2025-11-05", "data_fim": "2025-11-10", "tipo_reserva": "Teste"
            })
            assert reserva_res.status_code == 201
            reserva_id = reserva_res.json()["reserva_id"]

            # 2. Testar busca que conflita: só deve retornar Carro B
            response = client.get(f"/veiculos/disponiveis/?data_inicio=2025-11-08&data_fim=2025-11-12")
            assert response.status_code == 200
            data = response.json()
            
            placas_retornadas = {v['placa'] for v in data}
            assert placa2 in placas_retornadas
            assert placa1 not in placas_retornadas

            # 3. Testar busca que NÃO conflita: deve retornar ambos os carros
            response = client.get(f"/veiculos/disponiveis/?data_inicio=2025-12-01&data_fim=2025-12-05")
            assert response.status_code == 200
            data = response.json()
            placas_retornadas = {v['placa'] for v in data}
            assert placa1 in placas_retornadas
            assert placa2 in placas_retornadas
        finally:
            # 4. Limpeza garantida (ordem correta: reserva -> dependentes)
            if reserva_id: client.delete(f"/reservas/{reserva_id}")
            if v1_id: client.delete(f"/veiculos/{v1_id}")
            if v2_id: client.delete(f"/veiculos/{v2_id}")
            if cliente_id: client.delete(f"/clientes/{cliente_id}")