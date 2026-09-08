from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, Enum as SQLEnum, ForeignKey, Integer, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class StatusConversa(str, Enum):
    ATIVA = "ATIVA"
    ARQUIVADA = "ARQUIVADA"
    ENCERRADA = "ENCERRADA"


class Conversa(Base):
    __tablename__ = "conversa"

    id_conversa: Mapped[int] = mapped_column(
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

    data_criacao: Mapped[datetime | None] = mapped_column(
        DateTime,
        server_default=text("CURRENT_TIMESTAMP")
    )

    data_atualizacao: Mapped[datetime | None] = mapped_column(
        DateTime,
        server_default=text("CURRENT_TIMESTAMP")
    )

    status: Mapped[StatusConversa] = mapped_column(
        SQLEnum(
            StatusConversa,
            name="status_conversa",
            native_enum=True
        ),
        nullable=False
    )

    mensagens = relationship(
        "Mensagem",
        back_populates="conversa",
        cascade="all, delete-orphan"
    )