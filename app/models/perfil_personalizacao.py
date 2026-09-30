from datetime import datetime

from sqlalchemy import Integer, DateTime, ForeignKey, String, Text, Boolean, text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class PerfilPersonalizacao(Base):
    __tablename__ = "perfil_personalizacao"

    id_perfil: Mapped[int] = mapped_column(
        Integer,
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
        unique=True,
        index=True
    )

    tom: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        server_default="ADAPTATIVO"
    )

    formalidade: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        server_default="ADAPTATIVA"
    )

    nivel_detalhe: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default="MEDIO"
    )

    usar_emojis: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("1")
    )

    estilo_resposta: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        server_default="NATURAL"
    )

    instrucoes_personais: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    data_criacao: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP")
    )

    data_atualizacao: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
        onupdate=datetime.now
    )