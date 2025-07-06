-- database/init/02_data.sql
INSERT INTO endereco (rua, bairro, cidade, estado, numero) VALUES
('Rua das Flores', 'Centro', 'São Paulo', 'SP', 123),
('Avenida Principal', 'Comercial', 'Rio de Janeiro', 'RJ', 456);

INSERT INTO pessoa (nome, email, telefone, tipo_pessoa, cpf, estado_civil, endereco_id) VALUES
('João da Silva', 'joao.silva@email.com', '11987654321', 'PF', '123.456.789-00', 'Solteiro', 1);

INSERT INTO pessoa (nome, email, telefone, tipo_pessoa, cnpj, endereco_id) VALUES
('ABC Corp', 'contato@abccorp.com', '21912345678', 'PJ', '12.345.678/0001-99', 2);

INSERT INTO veiculo (placa, modelo, marca, ano, valor_diaria) VALUES
('ABC-1234', 'Gol', 'Volkswagen', 2022, 150.00),
('XYZ-5678', 'Mobi', 'Fiat', 2023, 130.50);

INSERT INTO reserva (data_inicio, data_fim, diarias, valor_total, tipo_reserva, cliente_id, veiculo_id) VALUES
('2025-06-22', '2025-06-25', 3, 450.00, 'Normal', 1, 1);