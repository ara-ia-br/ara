from datetime import datetime

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.conversa import Conversa, StatusConversa


class ConversaRepository:

    @staticmethod
    def criar(
        db: Session,
        conversa: Conversa
    ) -> Conversa:

        db.add(conversa)
        db.commit()
        db.refresh(conversa)

        return conversa

    @staticmethod
    def buscar_por_id(
        db: Session,
        id_conversa: int
    ) -> Conversa | None:

        return db.get(
            Conversa,
            id_conversa
        )

    @staticmethod
    def listar_por_usuario(
        db: Session,
        id_usuario: int
    ) -> list[Conversa]:

        resultado = db.execute(
            select(Conversa)
            .where(
                Conversa.id_usuario == id_usuario,
                Conversa.status != StatusConversa.ARQUIVADA
            )
            .order_by(
                Conversa.data_atualizacao.desc()
            )
        )

        return list(
            resultado.scalars().all()
        )

    @staticmethod
    def salvar(
        db: Session,
        conversa: Conversa
    ) -> Conversa:

        conversa.data_atualizacao = datetime.now()

        db.add(conversa)
        db.commit()
        db.refresh(conversa)

        return conversa

    @staticmethod
    def atualizar_data(
        db: Session,
        conversa: Conversa
    ) -> Conversa:

        conversa.data_atualizacao = datetime.now()

        db.commit()
        db.refresh(conversa)

        return conversa

    @staticmethod
    def excluir(
        db: Session,
        conversa: Conversa
    ) -> None:

        db.delete(conversa)
        db.commit()


    @staticmethod
    def listar_arquivadas_por_usuario(
            db: Session,
            id_usuario: int
    ) -> list[Conversa]:
        resultado = db.execute(
            select(Conversa)
            .where(
                Conversa.id_usuario == id_usuario,
                Conversa.status == StatusConversa.ARQUIVADA
            )
            .order_by(
                Conversa.data_atualizacao.desc()
            )
        )

        return list(
            resultado.scalars().all()
        )