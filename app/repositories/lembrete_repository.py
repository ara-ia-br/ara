from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.lembrete import Lembrete


class LembreteRepository:

    @staticmethod
    def criar(
        db: Session,
        lembrete: Lembrete
    ) -> Lembrete:

        db.add(lembrete)
        db.commit()
        db.refresh(lembrete)

        return lembrete

    @staticmethod
    def buscar_por_id(
        db: Session,
        id_lembrete: int
    ) -> Lembrete | None:

        return db.get(
            Lembrete,
            id_lembrete
        )

    @staticmethod
    def listar_por_usuario(
        db: Session,
        id_usuario: int
    ) -> list[Lembrete]:

        resultado = db.execute(
            select(Lembrete)
            .where(
                Lembrete.id_usuario == id_usuario
            )
            .order_by(
                Lembrete.data_hora.asc()
            )
        )

        return list(
            resultado.scalars().all()
        )

    @staticmethod
    def listar_pendentes(
            db: Session,
            id_usuario: int
    ) -> list[Lembrete]:
        resultado = db.execute(
            select(Lembrete)
            .where(
                Lembrete.id_usuario == id_usuario,
                Lembrete.status.in_([
                    "PENDENTE",
                    "EM_ANDAMENTO"
                ])
            )
            .order_by(
                Lembrete.data_hora.asc()
            )
        )

        return list(
            resultado.scalars().all()
        )

    @staticmethod
    def buscar_por_titulo(
            db: Session,
            id_usuario: int,
            titulo: str
    ) -> Lembrete | None:
        resultado = db.execute(
            select(Lembrete)
            .where(
                Lembrete.id_usuario == id_usuario,
                Lembrete.titulo.ilike(
                    f"%{titulo}%"
                ),
                Lembrete.status.in_([
                    "PENDENTE",
                    "EM_ANDAMENTO"
                ])
            )
            .order_by(
                Lembrete.data_hora.asc()
            )
        )

        return resultado.scalars().first()

    @staticmethod
    def salvar(
            db: Session,
            lembrete: Lembrete
    ) -> Lembrete:
        db.add(lembrete)
        db.commit()
        db.refresh(lembrete)

        return lembrete