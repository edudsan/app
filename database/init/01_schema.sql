-- database/init/01_schema.sql
CREATE TABLE endereco (
    endereco_id SERIAL PRIMARY KEY,
    rua VARCHAR(255) NOT NULL,
    bairro VARCHAR(100),
    cidade VARCHAR(100) NOT NULL,
    estado VARCHAR(2) NOT NULL,
    numero INT
);

CREATE TABLE pessoa (
    pessoa_id SERIAL PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    telefone VARCHAR(20),
    tipo_pessoa VARCHAR(2) NOT NULL CHECK (tipo_pessoa IN ('PF', 'PJ')),
    cpf VARCHAR(14) UNIQUE,
    estado_civil VARCHAR(50),
    cnpj VARCHAR(18) UNIQUE,
    endereco_id INT,
    CONSTRAINT fk_endereco
        FOREIGN KEY(endereco_id) 
        REFERENCES endereco(endereco_id)
);

CREATE TABLE veiculo (
    veiculo_id SERIAL PRIMARY KEY,
    placa VARCHAR(10) UNIQUE NOT NULL,
    modelo VARCHAR(100) NOT NULL,
    marca VARCHAR(100),
    ano INT,
    valor_diaria NUMERIC(10, 2) NOT NULL
);

CREATE TABLE reserva (
    reserva_id SERIAL PRIMARY KEY,
    data_inicio DATE NOT NULL,
    data_fim DATE NOT NULL,
    diarias INT NOT NULL,
    valor_total NUMERIC(10, 2) NOT NULL,
    tipo_reserva VARCHAR(50) NOT NULL,
    cliente_id INT NOT NULL,
    veiculo_id INT NOT NULL,
    CONSTRAINT fk_cliente
        FOREIGN KEY(cliente_id) 
        REFERENCES pessoa(pessoa_id),
    CONSTRAINT fk_veiculo
        FOREIGN KEY(veiculo_id) 
        REFERENCES veiculo(veiculo_id),
    CONSTRAINT chk_datas CHECK (data_fim > data_inicio)
);