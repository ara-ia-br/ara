from logging.config import fileConfig

from alembic import context

from app.database.base import Base
from app.database.connection import engine

# Importar todos os models para registrar as tabelas
# no Base.metadata usado pelo autogenerate.
import app.models.usuario
import app.models.conversa
import app.models.mensagem
import app.models.memoria
import app.models.tarefa
import app.models.lembrete
import app.models.contexto_agente
import app.models.entidade_contextual
import app.models.perfil_personalizacao


config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)


target_metadata = Base.metadata


def run_migrations_offline() -> None:

    url = engine.url.render_as_string(
        hide_password=False
    )

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={
            "paramstyle": "named"
        },
        compare_type=True,
        compare_server_default=True
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:

    with engine.connect() as connection:

        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()