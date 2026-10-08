from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    BigInteger,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    text,
)

from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Arquivo(Base):

    __tablename__ = "arquivo"

    id_arquivo: Mapped[int] = mapped_column(
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
        nullable=False,
        index=True
    )

    id_conversa: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey(
            "conversa.id_conversa",
            ondelete="SET NULL"
        ),
        nullable=True,
        index=True
    )

    nome_original: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    nome_armazenado: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True
    )

    mime_type: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True
    )

    extensao: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    tamanho_bytes: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        default=0
    )

    caminho: Mapped[str] = mapped_column(
        String(500),
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="ENVIADO",
        index=True
    )

    texto_extraido: Mapped[str | None] = mapped_column(
        LONGTEXT,
        nullable=True
    )

    erro_processamento: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    criado_em: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=text(
            "CURRENT_TIMESTAMP"
        )
    )

    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=text(
            "CURRENT_TIMESTAMP"
        ),
        server_onupdate=text(
            "CURRENT_TIMESTAMP"
        )
    )