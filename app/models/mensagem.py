from datetime import datetime
from decimal import Decimal
from enum import Enum

from sqlalchemy import (
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    text
)
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class RemetenteMensagem(str, Enum):
    USUARIO = "USUARIO"
    ARA = "ARA"
    SISTEMA = "SISTEMA"


class Mensagem(Base):
    __tablename__ = "mensagem"

    id_mensagem: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    id_conversa: Mapped[int] = mapped_column(
        ForeignKey("conversa.id_conversa"),
        nullable=False
    )

    remetente: Mapped[RemetenteMensagem] = mapped_column(
        SQLEnum(
            RemetenteMensagem,
            name="remetente_mensagem",
            native_enum=True
        ),
        nullable=False
    )

    conteudo: Mapped[str] = mapped_column(
        LONGTEXT,
        nullable=False
    )

    tipo: Mapped[str] = mapped_column(
        String(30),
        nullable=False
    )

    data_envio: Mapped[datetime | None] = mapped_column(
        DateTime,
        server_default=text("CURRENT_TIMESTAMP")
    )

    modelo_ia: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    tokens_entrada: Mapped[int] = mapped_column(
        Integer,
        server_default=text("0")
    )

    tokens_saida: Mapped[int] = mapped_column(
        Integer,
        server_default=text("0")
    )

    tempo_processamento: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 3),
        nullable=True
    )

    conversa = relationship(
        "Conversa",
        back_populates="mensagens"
    )