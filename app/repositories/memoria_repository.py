from datetime import datetime

from sqlalchemy import (
    or_,
    select
)

from sqlalchemy.orm import Session

from app.models.memoria import (
    Memoria
)


class MemoriaRepository:

    # =========================================================
    # CRIAR
    # =========================================================

    @staticmethod
    def criar(
        db: Session,
        memoria: Memoria
    ) -> Memoria:

        db.add(
            memoria
        )

        db.commit()

        db.refresh(
            memoria
        )

        return memoria


    # =========================================================
    # SALVAR / ATUALIZAR
    # =========================================================

    @staticmethod
    def salvar(
        db: Session,
        memoria: Memoria
    ) -> Memoria:

        db.add(
            memoria
        )

        db.commit()

        db.refresh(
            memoria
        )

        return memoria


    # =========================================================
    # BUSCAR POR ID
    # =========================================================

    @staticmethod
    def buscar_por_id(
        db: Session,
        id_memoria: int
    ) -> Memoria | None:

        return db.get(
            Memoria,
            id_memoria
        )


    # =========================================================
    # LISTAR MEMÓRIAS ATIVAS DO USUÁRIO
    # =========================================================

    @staticmethod
    def listar_ativas_usuario(
        db: Session,
        id_usuario: int
    ) -> list[Memoria]:

        agora = datetime.now()

        resultado = db.execute(
            select(
                Memoria
            )
            .where(
                Memoria.id_usuario
                == id_usuario,

                Memoria.ativa
                .is_(True),

                or_(
                    Memoria.data_expiracao
                    .is_(None),

                    Memoria.data_expiracao
                    > agora
                )
            )
            .order_by(
                Memoria.importancia.desc(),
                Memoria.data_atualizacao.desc(),
                Memoria.id_memoria.desc()
            )
        )

        return list(
            resultado
            .scalars()
            .all()
        )


    # =========================================================
    # LISTAR TODAS AS MEMÓRIAS DO USUÁRIO
    # =========================================================

    @staticmethod
    def listar_por_usuario(
        db: Session,
        id_usuario: int
    ) -> list[Memoria]:

        resultado = db.execute(
            select(
                Memoria
            )
            .where(
                Memoria.id_usuario
                == id_usuario
            )
            .order_by(
                Memoria.ativa.desc(),
                Memoria.importancia.desc(),
                Memoria.data_atualizacao.desc(),
                Memoria.id_memoria.desc()
            )
        )

        return list(
            resultado
            .scalars()
            .all()
        )


    # =========================================================
    # LISTAR MEMÓRIAS ATIVAS POR TIPO
    # =========================================================

    @staticmethod
    def listar_ativas_por_tipo(
        db: Session,
        id_usuario: int,
        tipo_memoria: str
    ) -> list[Memoria]:

        agora = datetime.now()

        resultado = db.execute(
            select(
                Memoria
            )
            .where(
                Memoria.id_usuario
                == id_usuario,

                Memoria.tipo_memoria
                == tipo_memoria,

                Memoria.ativa
                .is_(True),

                or_(
                    Memoria.data_expiracao
                    .is_(None),

                    Memoria.data_expiracao
                    > agora
                )
            )
            .order_by(
                Memoria.importancia.desc(),
                Memoria.data_atualizacao.desc(),
                Memoria.id_memoria.desc()
            )
        )

        return list(
            resultado
            .scalars()
            .all()
        )


    # =========================================================
    # BUSCAR CONTEÚDO EXATO
    # =========================================================

    @staticmethod
    def buscar_conteudo(
        db: Session,
        id_usuario: int,
        conteudo: str
    ) -> Memoria | None:

        resultado = db.execute(
            select(
                Memoria
            )
            .where(
                Memoria.id_usuario
                == id_usuario,

                Memoria.conteudo
                == conteudo,

                Memoria.ativa
                .is_(True)
            )
            .order_by(
                Memoria.data_atualizacao.desc(),
                Memoria.id_memoria.desc()
            )
        )

        return (
            resultado
            .scalars()
            .first()
        )


    # =========================================================
    # BUSCAR CONTEÚDO EXATO POR TIPO
    # =========================================================

    @staticmethod
    def buscar_conteudo_por_tipo(
        db: Session,
        id_usuario: int,
        tipo_memoria: str,
        conteudo: str
    ) -> Memoria | None:

        resultado = db.execute(
            select(
                Memoria
            )
            .where(
                Memoria.id_usuario
                == id_usuario,

                Memoria.tipo_memoria
                == tipo_memoria,

                Memoria.conteudo
                == conteudo,

                Memoria.ativa
                .is_(True)
            )
            .order_by(
                Memoria.data_atualizacao.desc(),
                Memoria.id_memoria.desc()
            )
        )

        return (
            resultado
            .scalars()
            .first()
        )


    # =========================================================
    # DESATIVAR
    # =========================================================

    @staticmethod
    def desativar(
        db: Session,
        memoria: Memoria
    ) -> Memoria:

        memoria.ativa = False

        db.add(
            memoria
        )

        db.commit()

        db.refresh(
            memoria
        )

        return memoria


    # =========================================================
    # REATIVAR
    # =========================================================

    @staticmethod
    def reativar(
        db: Session,
        memoria: Memoria
    ) -> Memoria:

        memoria.ativa = True

        db.add(
            memoria
        )

        db.commit()

        db.refresh(
            memoria
        )

        return memoria


    # =========================================================
    # DESATIVAR VÁRIAS
    #
    # Usaremos na consolidação:
    #
    # memória antiga:
    # "Usuário prefere estudar à noite."
    #
    # nova:
    # "Usuário prefere estudar de manhã."
    #
    # A antiga pode ser desativada.
    # =========================================================

    @staticmethod
    def desativar_varias(
        db: Session,
        memorias: list[Memoria]
    ) -> None:

        if not memorias:
            return

        for memoria in memorias:

            memoria.ativa = False

            db.add(
                memoria
            )

        db.commit()


    # =========================================================
    # ATUALIZAR IMPORTÂNCIA
    # =========================================================

    @staticmethod
    def atualizar_importancia(
        db: Session,
        memoria: Memoria,
        importancia
    ) -> Memoria:

        memoria.importancia = importancia

        db.add(
            memoria
        )

        db.commit()

        db.refresh(
            memoria
        )

        return memoria


    # =========================================================
    # EXCLUIR DEFINITIVAMENTE
    #
    # Deve ser usado apenas quando o usuário realmente
    # solicitar exclusão da memória.
    # Normalmente preferimos desativar.
    # =========================================================

    @staticmethod
    def excluir(
        db: Session,
        memoria: Memoria
    ) -> None:

        db.delete(
            memoria
        )

        db.commit()