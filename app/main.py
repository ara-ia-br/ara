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

app.include_router(usuario_router)
app.include_router(auth_router)
app.include_router(conversa_router)
app.include_router(mensagem_router)
app.include_router(chat_router)
app.include_router(memoria_router)
app.include_router(tarefa_router)


@app.get("/health")
def health_check():
    return {
        "status": "online",
        "system": "A.R.A."
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


# === FRONTEND A.R.A. ===
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

FRONTEND_DIST = Path(
    "/kaggle/working/ara/frontend/dist"
)

if FRONTEND_DIST.exists():

    assets_dir = FRONTEND_DIST / "assets"

    if assets_dir.exists():
        app.mount(
            "/assets",
            StaticFiles(
                directory=assets_dir
            ),
            name="frontend-assets"
        )

    @app.get("/")
    async def frontend_root():
        return FileResponse(
            FRONTEND_DIST / "index.html"
        )

    @app.get("/{full_path:path}")
    async def frontend_spa(full_path: str):

        arquivo = FRONTEND_DIST / full_path

        if (
            full_path
            and arquivo.exists()
            and arquivo.is_file()
        ):
            return FileResponse(arquivo)

        return FileResponse(
            FRONTEND_DIST / "index.html"
        )
