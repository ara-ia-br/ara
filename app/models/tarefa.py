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


class StatusTarefa(str, Enum):
    PENDENTE = "PENDENTE"
    EM_ANDAMENTO = "EM_ANDAMENTO"
    CONCLUIDA = "CONCLUIDA"
    CANCELADA = "CANCELADA"


class Tarefa(Base):
    __tablename__ = "tarefa"

    id_tarefa: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    id_usuario: Mapped[int] = mapped_column(
        ForeignKey("usuario.id_usuario"),
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

    prioridade: Mapped[int] = mapped_column(
        Integer,
        server_default=text("3")
    )

    status: Mapped[StatusTarefa] = mapped_column(
        SQLEnum(
            StatusTarefa,
            native_enum=True
        ),
        server_default=text("'PENDENTE'")
    )

    data_criacao: Mapped[datetime | None] = mapped_column(
        DateTime,
        server_default=text("CURRENT_TIMESTAMP")
    )

    data_inicio: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    data_conclusao: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    data_limite: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )