from fastapi import FastAPI
from sqlalchemy import text

from app.api.usuario_router import router as usuario_router
from app.database.connection import engine
from app.api.auth_router import router as auth_router
from app.api.conversa_router import router as conversa_router
from app.api.mensagem_router import router as mensagem_router
from app.api.chat_router import router as chat_router
from app.api.memoria_router import router as memoria_router
from app.agent.tools.register import registrar_tools
from fastapi.middleware.cors import CORSMiddleware
from app.api.tarefa_router import router as tarefa_router
from app.api.projeto_router import router as projeto_router
from app.api.agenda_router import router as agenda_router



app = FastAPI(
    title="JARVIS",
    description="Assistente de Inteligência Artificial",
    version="1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

registrar_tools()


def preparar_estrutura_projetos():
    """Cria a estrutura de projetos sem exigir que o usuário recrie o banco."""
    with engine.begin() as connection:
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS projeto (
                id_projeto INT NOT NULL AUTO_INCREMENT,
                id_usuario INT NOT NULL,
                nome VARCHAR(120) NOT NULL,
                descricao TEXT NULL,
                data_criacao DATETIME NULL DEFAULT CURRENT_TIMESTAMP,
                data_atualizacao DATETIME NULL DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (id_projeto),
                KEY idx_projeto_usuario (id_usuario),
                CONSTRAINT fk_projeto_usuario FOREIGN KEY (id_usuario)
                    REFERENCES usuario (id_usuario) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """))

        coluna = connection.execute(text("""
            SELECT COUNT(*)
            FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE()
              AND TABLE_NAME = 'conversa'
              AND COLUMN_NAME = 'id_projeto'
        """)).scalar()

        if not coluna:
            connection.execute(text("""
                ALTER TABLE conversa
                ADD COLUMN id_projeto INT NULL,
                ADD KEY idx_conversa_projeto (id_projeto)
            """))

        constraint = connection.execute(text("""
            SELECT COUNT(*)
            FROM information_schema.TABLE_CONSTRAINTS
            WHERE CONSTRAINT_SCHEMA = DATABASE()
              AND TABLE_NAME = 'conversa'
              AND CONSTRAINT_NAME = 'fk_conversa_projeto'
        """)).scalar()

        if not constraint:
            connection.execute(text("""
                ALTER TABLE conversa
                ADD CONSTRAINT fk_conversa_projeto
                FOREIGN KEY (id_projeto)
                REFERENCES projeto (id_projeto)
                ON DELETE SET NULL
            """))


def preparar_estrutura_agenda():
    """Garante que a tabela usada pela Agenda exista no banco atual."""
    with engine.begin() as connection:
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS lembrete (
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
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """))


preparar_estrutura_projetos()
preparar_estrutura_agenda()

app.include_router(usuario_router)
app.include_router(auth_router)
app.include_router(conversa_router)
app.include_router(mensagem_router)
app.include_router(chat_router)
app.include_router(memoria_router)
app.include_router(tarefa_router)
app.include_router(projeto_router)
app.include_router(agenda_router)


@app.get("/health")
def health_check():
    return {
        "status": "online",
        "system": "JARVIS"
    }


# CONEXÃO MYSQL
@app.get("/database")
def database():
    with engine.connect() as connection:
        version = connection.execute(
            text("SELECT VERSION()")
        ).scalar()

    return {
        "database": "connected",
        "mysql_version": version
    }


@app.get("/database/usuario")
def usuario_check():
    with engine.connect() as conn:
        resultado = conn.execute(
            text(
                "SELECT id_usuario, nome, email, ativo "
                "FROM usuario"
            )
        )

        usuarios = [
            {
                "id_usuario": row.id_usuario,
                "nome": row.nome,
                "email": row.email,
                "ativo": bool(row.ativo)
            }
            for row in resultado
        ]

    return usuarios