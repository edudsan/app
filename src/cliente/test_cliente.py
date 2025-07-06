# src/cliente/test_cliente.py
import uuid
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def unique_suffix():
    return uuid.uuid4().hex[:6]

class TestClientes:
    def test_ciclo_de_vida_cliente_pf(self):
        # Gera dados únicos para esta execução de teste
        suffix = unique_suffix()
        email = f"jose.pf.{suffix}@teste.com"
        cpf = f"111.222.333-{suffix[:2]}"
        pessoa_id = None
        try:
            # 1. Criar
            novo_cliente = {
                "nome": "José Teste PF", "email": email, "cpf": cpf,
                "endereco": {"rua": "Rua Teste PF", "cidade": "Teste", "estado": "TS"}
            }
            resposta = client.post("/clientes/pf", json=novo_cliente)
            assert resposta.status_code == 201, resposta.text
            dados = resposta.json()
            pessoa_id = dados["pessoa_id"]
            assert dados["email"] == email

            # 2. Ler
            resposta = client.get(f"/clientes/{pessoa_id}")
            assert resposta.status_code == 200
            assert resposta.json()["nome"] == "José Teste PF"

            # 3. Atualizar
            dados_atualizados = {"telefone": "99999-8888", 
            "endereco": {"cidade": "Cidade Alterada"}}
            resposta = client.put(f"/clientes/{pessoa_id}", json=dados_atualizados)
            assert resposta.status_code == 200
            assert resposta.json()["telefone"] == "99999-8888"
            assert resposta.json()["endereco"]["cidade"] == "Cidade Alterada"

        finally:
            # 4. Limpeza (executa mesmo se os asserts falharem)
            if pessoa_id:
                client.delete(f"/clientes/{pessoa_id}")

    def test_criar_email_duplicado(self):
        suffix = unique_suffix()
        email = f"duplicado.{suffix}@teste.com"
        cpf1 = f"123.123.123-{suffix[:2]}"
        cpf2 = f"456.456.456-{suffix[:2]}"
        pessoa_id = None
        try:
            locatario1 = {
                "nome": "Primeiro Dono", "email": email, "cpf": cpf1,
                "endereco": {"rua": "Rua A", "cidade": "C", "estado": "E"}
            }
            resposta1 = client.post("/clientes/pf", json=locatario1)
            assert resposta1.status_code == 201
            pessoa_id = resposta1.json()["pessoa_id"]

            locatario2 = {
                "nome": "Segundo Dono", "email": email, "cpf": cpf2,
                "endereco": {"rua": "Rua B", "cidade": "C", "estado": "E"}
            }
            resposta2 = client.post("/clientes/pf", json=locatario2)
            assert resposta2.status_code == 409
        finally:
            if pessoa_id:
                client.delete(f"/clientes/{pessoa_id}")