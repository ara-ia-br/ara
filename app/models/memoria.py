from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    text,
)
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Memoria(Base):
    __tablename__ = "memoria"

    id_memoria: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    id_usuario: Mapped[int] = mapped_column(
        ForeignKey("usuario.id_usuario"),
        nullable=False
    )

    tipo_memoria: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    conteudo: Mapped[str] = mapped_column(
        LONGTEXT,
        nullable=False
    )

    importancia: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        nullable=False,
        server_default=text("0.00")
    )

    data_criacao: Mapped[datetime | None] = mapped_column(
        DateTime,
        server_default=text("CURRENT_TIMESTAMP")
    )

    data_atualizacao: Mapped[datetime | None] = mapped_column(
        DateTime,
        server_default=text("CURRENT_TIMESTAMP")
    )

    data_expiracao: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    ativa: Mapped[bool] = mapped_column(
        Boolean,
        server_default=text("1")
    )