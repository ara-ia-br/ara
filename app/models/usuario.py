from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Usuario(Base):
    __tablename__ = "usuario"

    id_usuario: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    nome: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    email: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        unique=True
    )

    senha: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    data_cadastro: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP")
    )

    data_ultimo_acesso: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    ativo: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("1")
    )