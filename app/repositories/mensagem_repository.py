from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.mensagem import Mensagem


class MensagemRepository:

    @staticmethod
    def criar(
        db: Session,
        mensagem: Mensagem
    ) -> Mensagem:

        db.add(mensagem)
        db.commit()
        db.refresh(mensagem)

        return mensagem

    @staticmethod
    def listar_por_conversa(
        db: Session,
        id_conversa: int
    ) -> list[Mensagem]:

        resultado = db.execute(
            select(Mensagem)
            .where(
                Mensagem.id_conversa == id_conversa
            )
            .order_by(
                Mensagem.data_envio.asc()
            )
        )

        return list(
            resultado.scalars().all()
        )