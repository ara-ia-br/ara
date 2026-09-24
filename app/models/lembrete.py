from datetime import datetime
from enum import Enum

from sqlalchemy import (
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Integer,
    String,
    Text,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class StatusLembrete(str, Enum):
    PENDENTE = "PENDENTE"
    EM_ANDAMENTO = "EM_ANDAMENTO"
    CONCLUIDA = "CONCLUIDA"
    CANCELADA = "CANCELADA"


class Lembrete(Base):
    __tablename__ = "lembrete"

    id_lembrete: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    id_usuario: Mapped[int] = mapped_column(
        ForeignKey("usuario.id_usuario"),
        nullable=False
    )

    id_tarefa: Mapped[int] = mapped_column(
        ForeignKey(
            "tarefa.id_tarefa",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    titulo: Mapped[str] = mapped_column(
        String(200),
        nullable=False
    )

    descricao: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    data_hora: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False
    )

    recorrencia: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    status: Mapped[StatusLembrete] = mapped_column(
        SQLEnum(
            StatusLembrete,
            native_enum=True
        ),
        server_default=text("'PENDENTE'")
    )

    data_criacao: Mapped[datetime | None] = mapped_column(
        DateTime,
        server_default=text("CURRENT_TIMESTAMP")
    )