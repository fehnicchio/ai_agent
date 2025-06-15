-- Criação do banco de dados com encoding correto
CREATE DATABASE empresa_db
    ENCODING 'UTF8'
    LC_COLLATE 'Portuguese_Brazil.1252'
    LC_CTYPE 'Portuguese_Brazil.1252';

-- Conecta ao banco
\c empresa_db

-- Tabela de clientes
CREATE TABLE clientes (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE,
    estado CHAR(2) NOT NULL,
    data_cadastro DATE DEFAULT CURRENT_DATE
);

-- Tabela de pedidos
CREATE TABLE pedidos (
    id SERIAL PRIMARY KEY,
    cliente_id INTEGER REFERENCES clientes(id),
    produto VARCHAR(50) NOT NULL,
    quantidade INTEGER NOT NULL CHECK (quantidade > 0),
    valor NUMERIC(10,2) NOT NULL,
    data_pedido DATE DEFAULT CURRENT_DATE
);

-- Inserção de dados de exemplo com encoding correto
INSERT INTO clientes (nome, email, estado) VALUES 
('João Silva', 'joao@empresa.com', 'SP'),
('Maria Santos', 'maria@empresa.com', 'RJ'),
('Carlos Oliveira', 'carlos@empresa.com', 'MG'),
('Ana Costa', 'ana@empresa.com', 'SP'),
('Pedro Alves', 'pedro@empresa.com', 'RJ'),
('Julia Pereira', 'julia@empresa.com', 'MG');

INSERT INTO pedidos (cliente_id, produto, quantidade, valor) VALUES
(1, 'Notebook Pro', 1, 4500.00),
(1, 'Mouse Sem Fio', 2, 120.50),
(2, 'Teclado Mecânico', 1, 350.00),
(3, 'Monitor 24"', 2, 1800.00),
(4, 'Webcam HD', 1, 280.90),
(5, 'Headphone Bluetooth', 1, 420.00),
(6, 'Tablet 10"', 1, 1500.00),
(1, 'Carregador Portátil', 1, 200.00),
(2, 'Hub USB', 1, 150.00);

-- Visualização para consultas
CREATE VIEW resumo_clientes AS
SELECT 
    c.id,
    c.nome,
    c.estado,
    COUNT(p.id) AS total_pedidos,
    SUM(p.valor) AS valor_total
FROM clientes c
LEFT JOIN pedidos p ON c.id = p.cliente_id
GROUP BY c.id;