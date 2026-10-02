from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Projeto(Base):
    __tablename__ = "projeto"

    id_projeto: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    id_usuario: Mapped[int] = mapped_column(
        ForeignKey("usuario.id_usuario", ondelete="CASCADE"),
        nullable=False
    )

    nome: Mapped[str] = mapped_column(
        String(120),
        nullable=False
    )

    descricao: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    data_criacao: Mapped[datetime | None] = mapped_column(
        DateTime,
        server_default=text("CURRENT_TIMESTAMP")
    )

    data_atualizacao: Mapped[datetime | None] = mapped_column(
        DateTime,
        server_default=text("CURRENT_TIMESTAMP")
    )
