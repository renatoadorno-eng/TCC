CREATE DATABASE IF NOT EXISTS sistema_epi;
USE sistema_epi;

CREATE TABLE Usuario (
    ID INT AUTO_INCREMENT PRIMARY KEY,
    Nome VARCHAR(100) NOT NULL,
    Email VARCHAR(100) UNIQUE NOT NULL,
    Senha VARCHAR(255) NOT NULL,
    Foto VARCHAR(255) DEFAULT NULL
);

CREATE TABLE Colaborador ( 
    ID INT AUTO_INCREMENT PRIMARY KEY,  
    Nome VARCHAR(100) NOT NULL,  
    Setor VARCHAR(50) NOT NULL,  
    ativo TINYINT DEFAULT 1
); 

CREATE TABLE Equipamento ( 
    ID INT AUTO_INCREMENT PRIMARY KEY,  
    Nome VARCHAR(100) NOT NULL,  
    QTD_estoque INT NOT NULL,  
    ativo TINYINT DEFAULT 1
); 

CREATE TABLE Emprestimo ( 
    ID INT PRIMARY KEY AUTO_INCREMENT,  
    Data DATETIME NOT NULL,  
    idColaborador INT NOT NULL,  
    Situacao BOOLEAN NOT NULL,
    status VARCHAR(50) DEFAULT 'Emprestado',
    data_prevista_devolucao DATETIME DEFAULT NULL,
    data_efetiva_devolucao DATETIME DEFAULT NULL,
    observacao_devolucao TEXT DEFAULT NULL,
    FOREIGN KEY (idColaborador) REFERENCES Colaborador(ID)  
); 

CREATE TABLE contem ( 
    idEmprestimo INT NOT NULL,  
    idEquipamento INT NOT NULL,  
    Quantidade INT NOT NULL,
    PRIMARY KEY (idEmprestimo, idEquipamento),
    FOREIGN KEY (idEmprestimo) REFERENCES Emprestimo(ID),
    FOREIGN KEY (idEquipamento) REFERENCES Equipamento(ID)  
);