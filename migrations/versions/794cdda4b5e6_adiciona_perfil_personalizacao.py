"""adiciona perfil personalizacao

Revision ID: 794cdda4b5e6
Revises: b553a628dade
Create Date: 2026-10-02 07:58:17.359631

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '794cdda4b5e6'
down_revision: Union[str, Sequence[str], None] = 'b553a628dade'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if "perfil_personalizacao" not in inspector.get_table_names():

        op.create_table(
            "perfil_personalizacao",

            sa.Column(
                "id_perfil",
                sa.Integer(),
                autoincrement=True,
                nullable=False
            ),

            sa.Column(
                "id_usuario",
                sa.Integer(),
                nullable=False
            ),

            sa.Column(
                "tom",
                sa.String(length=30),
                server_default="ADAPTATIVO",
                nullable=False
            ),

            sa.Column(
                "formalidade",
                sa.String(length=30),
                server_default="ADAPTATIVA",
                nullable=False
            ),

            sa.Column(
                "nivel_detalhe",
                sa.String(length=20),
                server_default="MEDIO",
                nullable=False
            ),

            sa.Column(
                "usar_emojis",
                sa.Boolean(),
                server_default=sa.text("1"),
                nullable=False
            ),

            sa.Column(
                "estilo_resposta",
                sa.String(length=30),
                server_default="NATURAL",
                nullable=False
            ),

            sa.Column(
                "instrucoes_personais",
                sa.Text(),
                nullable=True
            ),

            sa.Column(
                "data_criacao",
                sa.DateTime(),
                server_default=sa.text("CURRENT_TIMESTAMP"),
                nullable=False
            ),

            sa.Column(
                "data_atualizacao",
                sa.DateTime(),
                server_default=sa.text("CURRENT_TIMESTAMP"),
                nullable=False
            ),

            sa.ForeignKeyConstraint(
                ["id_usuario"],
                ["usuario.id_usuario"],
                ondelete="CASCADE"
            ),

            sa.PrimaryKeyConstraint(
                "id_perfil"
            )
        )

        op.create_index(
            op.f(
                "ix_perfil_personalizacao_id_usuario"
            ),
            "perfil_personalizacao",
            ["id_usuario"],
            unique=True
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if "perfil_personalizacao" in inspector.get_table_names():

        indexes = {
            indice["name"]
            for indice
            in inspector.get_indexes(
                "perfil_personalizacao"
            )
        }

        if (
            "ix_perfil_personalizacao_id_usuario"
            in indexes
        ):
            op.drop_index(
                op.f(
                    "ix_perfil_personalizacao_id_usuario"
                ),
                table_name="perfil_personalizacao"
            )

        op.drop_table(
            "perfil_personalizacao"
        )
