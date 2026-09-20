from datetime import datetime

from sqlalchemy import (
    BigInteger,
    DateTime,
    ForeignKey,
    Integer,
    String,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column
)

from app.database.base import Base


class EntidadeContextual(Base):

    __tablename__ = "entidade_contextual"

    id_entidade_contextual: Mapped[int] = mapped_column(
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
        nullable=False
    )

    tipo_entidade: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    id_entidade: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    titulo: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    ordem_contexto: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False
    )

    data_mencao: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        nullable=False
    )
