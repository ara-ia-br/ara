"""adiciona dados visuais em mensagem

Revision ID: a7557ff28479
Revises: 794cdda4b5e6
Create Date: 2026-10-02 16:53:12.142793

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a7557ff28479'
down_revision: Union[str, Sequence[str], None] = '794cdda4b5e6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "mensagem",
        sa.Column(
            "dados_visuais",
            sa.JSON(),
            nullable=True
        )
    )


def downgrade() -> None:
    op.drop_column(
        "mensagem",
        "dados_visuais"
    )