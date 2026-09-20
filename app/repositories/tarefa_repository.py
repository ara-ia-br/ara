from datetime import datetime
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.tarefa import (
    StatusTarefa,
    Tarefa
)


class TarefaRepository:

    # =========================================================
    # CRIAR
    # =========================================================

    @staticmethod
    def criar(
        db: Session,
        tarefa: Tarefa
    ) -> Tarefa:

        db.add(tarefa)
        db.commit()
        db.refresh(tarefa)

        return tarefa


    # =========================================================
    # BUSCAR POR ID
    # =========================================================

    @staticmethod
    def buscar_por_id(
        db: Session,
        id_tarefa: int
    ) -> Tarefa | None:

        return db.get(
            Tarefa,
            id_tarefa
        )


    # =========================================================
    # BUSCAR POR TÍTULO
    # =========================================================

    @staticmethod
    def buscar_por_titulo(
        db: Session,
        id_usuario: int,
        titulo: str
    ) -> Tarefa | None:

        titulo = titulo.strip()

        if not titulo:
            return None


        # -----------------------------------------------------
        # 1. TENTA BUSCA EXATA
        # -----------------------------------------------------

        resultado_exato = db.execute(
            select(Tarefa)
            .where(
                Tarefa.id_usuario == id_usuario,
                Tarefa.titulo.ilike(titulo)
            )
            .order_by(
                Tarefa.id_tarefa.desc()
            )
        )

        tarefa = (
            resultado_exato
            .scalars()
            .first()
        )


        if tarefa is not None:
            return tarefa


        # -----------------------------------------------------
        # 2. TENTA BUSCA PARCIAL
        # -----------------------------------------------------

        resultado_parcial = db.execute(
            select(Tarefa)
            .where(
                Tarefa.id_usuario == id_usuario,
                Tarefa.titulo.ilike(
                    f"%{titulo}%"
                )
            )
            .order_by(
                Tarefa.id_tarefa.desc()
            )
        )

        return (
            resultado_parcial
            .scalars()
            .first()
        )


    # =========================================================
    # LISTAR POR USUÁRIO
    # =========================================================

    @staticmethod
    def listar_por_usuario(
        db: Session,
        id_usuario: int
    ) -> list[Tarefa]:

        resultado = db.execute(
            select(Tarefa)
            .where(
                Tarefa.id_usuario == id_usuario
            )
            .order_by(
                Tarefa.data_criacao.desc()
            )
        )

        return list(
            resultado.scalars().all()
        )


    # =========================================================
    # LISTAR POR STATUS
    # =========================================================

    @staticmethod
    def listar_por_status(
        db: Session,
        id_usuario: int,
        status: StatusTarefa
    ) -> list[Tarefa]:

        resultado = db.execute(
            select(Tarefa)
            .where(
                Tarefa.id_usuario == id_usuario,
                Tarefa.status == status
            )
            .order_by(
                Tarefa.data_criacao.desc()
            )
        )

        return list(
            resultado.scalars().all()
        )


    # =========================================================
    # SALVAR
    # =========================================================

    @staticmethod
    def salvar(
        db: Session,
        tarefa: Tarefa
    ) -> Tarefa:

        db.add(tarefa)

        db.commit()

        db.refresh(tarefa)

        return tarefa


    # =========================================================
    # EXCLUIR
    # =========================================================

    @staticmethod
    def excluir(
        db: Session,
        tarefa: Tarefa
    ) -> None:

        db.delete(tarefa)

        db.commit()

    @staticmethod
    def listar_por_periodo(
            db: Session,
            id_usuario: int,
            inicio: datetime,
            fim: datetime
    ) -> list[Tarefa]:

        resultado = db.execute(
            select(Tarefa)
            .where(
                Tarefa.id_usuario == id_usuario,
                Tarefa.data_limite.is_not(None),
                Tarefa.data_limite >= inicio,
                Tarefa.data_limite <= fim
            )
            .order_by(
                Tarefa.data_limite.asc()
            )
        )

        return list(
            resultado.scalars().all()
        )