from datetime import datetime

from sqlalchemy import (
    Integer,
    BigInteger,
    DateTime,
    ForeignKey,
    String,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column
)

from app.database.base import Base


class ContextoAgente(Base):

    __tablename__ = "contexto_agente"

    id_contexto: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True
    )

    id_usuario: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(
            "usuario.id_usuario",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    id_conversa: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(
            "conversa.id_conversa",
            ondelete="CASCADE"
        ),
        nullable=False,
        unique=True
    )

    ultima_tarefa_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey(
            "tarefa.id_tarefa",
            ondelete="SET NULL"
        ),
        nullable=True
    )

    ultimo_lembrete_id: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    ultima_ferramenta: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    data_atualizacao: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now,
        nullable=False
    )
