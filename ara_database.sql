-- ============================================================
-- JARVIS / A.R.A. - BANCO DE DADOS OFICIAL DO BACKEND
-- Snapshot reconstruido a partir do backend real do projeto
-- Banco: MySQL / MariaDB
-- Nome historico do banco: jarvis
-- ============================================================



CREATE DATABASE IF NOT EXISTS ara
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE ara;

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS entidade_contextual;
DROP TABLE IF EXISTS contexto_agente;
DROP TABLE IF EXISTS lembrete;
DROP TABLE IF EXISTS mensagem;
DROP TABLE IF EXISTS memoria;
DROP TABLE IF EXISTS tarefa;
DROP TABLE IF EXISTS conversa;
DROP TABLE IF EXISTS usuario;

SET FOREIGN_KEY_CHECKS = 1;

CREATE TABLE usuario (
    id_usuario INT NOT NULL AUTO_INCREMENT,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL,
    senha VARCHAR(255) NOT NULL,
    data_cadastro DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    data_ultimo_acesso DATETIME NULL,
    ativo BOOLEAN NOT NULL DEFAULT TRUE,
    PRIMARY KEY (id_usuario),
    UNIQUE KEY uk_usuario_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE conversa (
    id_conversa INT NOT NULL AUTO_INCREMENT,
    id_usuario INT NOT NULL,
    titulo VARCHAR(200) NULL,
    data_criacao DATETIME NULL DEFAULT CURRENT_TIMESTAMP,
    data_atualizacao DATETIME NULL DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(9) NOT NULL DEFAULT 'ATIVA',
    PRIMARY KEY (id_conversa),
    KEY idx_conversa_usuario (id_usuario),
    KEY idx_conversa_status (status),
    CONSTRAINT fk_conversa_usuario FOREIGN KEY (id_usuario)
        REFERENCES usuario (id_usuario) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE mensagem (
    id_mensagem INT NOT NULL AUTO_INCREMENT,
    id_conversa INT NOT NULL,
    remetente VARCHAR(10) NOT NULL,
    conteudo TEXT NOT NULL,
    tipo VARCHAR(50) NOT NULL DEFAULT 'TEXTO',
    data_envio DATETIME NULL DEFAULT CURRENT_TIMESTAMP,
    modelo_ia VARCHAR(100) NULL,
    tokens_entrada INT NULL,
    tokens_saida INT NULL,
    tempo_processamento FLOAT NULL,
    PRIMARY KEY (id_mensagem),
    KEY idx_mensagem_conversa (id_conversa),
    KEY idx_mensagem_data_envio (data_envio),
    CONSTRAINT fk_mensagem_conversa FOREIGN KEY (id_conversa)
        REFERENCES conversa (id_conversa) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE memoria (
    id_memoria INT NOT NULL AUTO_INCREMENT,
    id_usuario INT NOT NULL,
    tipo_memoria VARCHAR(50) NOT NULL,
    conteudo TEXT NOT NULL,
    importancia DECIMAL(5,2) NOT NULL DEFAULT 50.00,
    data_criacao DATETIME NULL DEFAULT CURRENT_TIMESTAMP,
    data_atualizacao DATETIME NULL DEFAULT CURRENT_TIMESTAMP,
    data_expiracao DATETIME NULL,
    ativa BOOLEAN NOT NULL DEFAULT TRUE,
    PRIMARY KEY (id_memoria),
    KEY idx_memoria_usuario (id_usuario),
    KEY idx_memoria_tipo (tipo_memoria),
    KEY idx_memoria_ativa (ativa),
    CONSTRAINT fk_memoria_usuario FOREIGN KEY (id_usuario)
        REFERENCES usuario (id_usuario) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE tarefa (
    id_tarefa INT NOT NULL AUTO_INCREMENT,
    id_usuario INT NOT NULL,
    titulo VARCHAR(200) NOT NULL,
    descricao TEXT NULL,
    prioridade INT NOT NULL DEFAULT 3,
    status VARCHAR(12) NOT NULL DEFAULT 'PENDENTE',
    data_criacao DATETIME NULL DEFAULT CURRENT_TIMESTAMP,
    data_inicio DATETIME NULL,
    data_conclusao DATETIME NULL,
    data_limite DATETIME NULL,
    PRIMARY KEY (id_tarefa),
    KEY idx_tarefa_usuario (id_usuario),
    KEY idx_tarefa_status (status),
    KEY idx_tarefa_data_limite (data_limite),
    CONSTRAINT fk_tarefa_usuario FOREIGN KEY (id_usuario)
        REFERENCES usuario (id_usuario) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE lembrete (
    id_lembrete INT NOT NULL AUTO_INCREMENT,
    id_usuario INT NOT NULL,
    id_tarefa INT NULL,
    titulo VARCHAR(200) NOT NULL,
    descricao TEXT NULL,
    data_hora DATETIME NOT NULL,
    recorrencia VARCHAR(100) NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'PENDENTE',
    data_criacao DATETIME NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id_lembrete),
    KEY idx_lembrete_usuario (id_usuario),
    KEY idx_lembrete_tarefa (id_tarefa),
    KEY idx_lembrete_data_hora (data_hora),
    KEY idx_lembrete_status (status),
    CONSTRAINT fk_lembrete_usuario FOREIGN KEY (id_usuario)
        REFERENCES usuario (id_usuario) ON DELETE CASCADE,
    CONSTRAINT fk_lembrete_tarefa FOREIGN KEY (id_tarefa)
        REFERENCES tarefa (id_tarefa) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE contexto_agente (
    id_contexto BIGINT NOT NULL AUTO_INCREMENT,
    id_usuario INT NOT NULL,
    id_conversa INT NOT NULL,
    ultima_tarefa_id INT NULL,
    ultimo_lembrete_id BIGINT NULL,
    ultima_ferramenta VARCHAR(100) NULL,
    data_atualizacao DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id_contexto),
    UNIQUE KEY uk_contexto_agente_conversa (id_conversa),
    KEY idx_contexto_agente_usuario (id_usuario),
    KEY idx_contexto_agente_tarefa (ultima_tarefa_id),
    CONSTRAINT fk_contexto_agente_usuario FOREIGN KEY (id_usuario)
        REFERENCES usuario (id_usuario) ON DELETE CASCADE,
    CONSTRAINT fk_contexto_agente_conversa FOREIGN KEY (id_conversa)
        REFERENCES conversa (id_conversa) ON DELETE CASCADE,
    CONSTRAINT fk_contexto_agente_tarefa FOREIGN KEY (ultima_tarefa_id)
        REFERENCES tarefa (id_tarefa) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE entidade_contextual (
    id_entidade_contextual BIGINT NOT NULL AUTO_INCREMENT,
    id_usuario INT NOT NULL,
    id_conversa INT NOT NULL,
    tipo_entidade VARCHAR(50) NOT NULL,
    id_entidade BIGINT NOT NULL,
    titulo VARCHAR(255) NULL,
    ordem_contexto INT NOT NULL DEFAULT 1,
    data_mencao DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id_entidade_contextual),
    KEY idx_entidade_contextual_usuario (id_usuario),
    KEY idx_entidade_contextual_conversa (id_conversa),
    KEY idx_entidade_contextual_tipo_id (tipo_entidade, id_entidade),
    CONSTRAINT fk_entidade_contextual_usuario FOREIGN KEY (id_usuario)
        REFERENCES usuario (id_usuario) ON DELETE CASCADE,
    CONSTRAINT fk_entidade_contextual_conversa FOREIGN KEY (id_conversa)
        REFERENCES conversa (id_conversa) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

SHOW TABLES;
