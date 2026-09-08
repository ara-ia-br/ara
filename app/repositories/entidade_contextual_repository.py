from sqlalchemy import (
    delete,
    select,
    update
)

from sqlalchemy.orm import Session

from app.models.entidade_contextual import (
    EntidadeContextual
)


class EntidadeContextualRepository:

    # =========================================================
    # CRIAR / REGISTRAR MENÇÃO
    # =========================================================

    @staticmethod
    def criar(
        db: Session,
        entidade: EntidadeContextual
    ) -> EntidadeContextual:

        try:

            # =================================================
            # 1. TODAS AS ENTIDADES ATUAIS DESCEM UMA POSIÇÃO
            #
            # Antes:
            #
            # Python = 1
            # Java   = 2
            #
            # usuário menciona Java:
            #
            # temporariamente:
            #
            # Python = 2
            # Java   = 3
            # =================================================

            db.execute(
                update(
                    EntidadeContextual
                )
                .where(
                    EntidadeContextual.id_usuario
                    == entidade.id_usuario,

                    EntidadeContextual.id_conversa
                    == entidade.id_conversa,

                    EntidadeContextual.tipo_entidade
                    == entidade.tipo_entidade
                )
                .values(
                    ordem_contexto=(
                        EntidadeContextual.ordem_contexto
                        + 1
                    )
                )
            )


            # =================================================
            # 2. SE A ENTIDADE JÁ EXISTIA NO CONTEXTO,
            # TODAS AS MENÇÕES DELA VOLTAM PARA O FOCO
            #
            # Java:
            # ordem 3
            #
            # vira:
            # ordem 1
            # =================================================

            db.execute(
                update(
                    EntidadeContextual
                )
                .where(
                    EntidadeContextual.id_usuario
                    == entidade.id_usuario,

                    EntidadeContextual.id_conversa
                    == entidade.id_conversa,

                    EntidadeContextual.tipo_entidade
                    == entidade.tipo_entidade,

                    EntidadeContextual.id_entidade
                    == entidade.id_entidade
                )
                .values(
                    ordem_contexto=1
                )
            )


            # =================================================
            # 3. NOVA MENÇÃO É SEMPRE O FOCO ATUAL
            # =================================================

            entidade.ordem_contexto = 1

            db.add(
                entidade
            )

            db.commit()

            db.refresh(
                entidade
            )

            return entidade


        except Exception:

            db.rollback()

            raise


    # =========================================================
    # LISTAR MENÇÕES RECENTES
    # =========================================================

    @staticmethod
    def listar_recentes(
        db: Session,
        id_usuario: int,
        id_conversa: int,
        tipo_entidade: str | None = None,
        limite: int = 10
    ) -> list[EntidadeContextual]:

        consulta = (
            select(
                EntidadeContextual
            )
            .where(
                EntidadeContextual.id_usuario
                == id_usuario,

                EntidadeContextual.id_conversa
                == id_conversa
            )
        )


        if tipo_entidade is not None:

            consulta = consulta.where(
                EntidadeContextual.tipo_entidade
                == tipo_entidade
            )


        consulta = (
            consulta
            .order_by(
                EntidadeContextual.data_mencao.desc(),
                EntidadeContextual.id_entidade_contextual.desc()
            )
            .limit(
                limite
            )
        )


        resultado = db.execute(
            consulta
        )


        return list(
            resultado
            .scalars()
            .all()
        )


    # =========================================================
    # LISTAR POR ORDEM DE FOCO
    # =========================================================

    @staticmethod
    def listar_por_foco(
        db: Session,
        id_usuario: int,
        id_conversa: int,
        tipo_entidade: str | None = None,
        limite: int = 20
    ) -> list[EntidadeContextual]:

        consulta = (
            select(
                EntidadeContextual
            )
            .where(
                EntidadeContextual.id_usuario
                == id_usuario,

                EntidadeContextual.id_conversa
                == id_conversa
            )
        )


        if tipo_entidade is not None:

            consulta = consulta.where(
                EntidadeContextual.tipo_entidade
                == tipo_entidade
            )


        consulta = (
            consulta
            .order_by(
                EntidadeContextual.ordem_contexto.asc(),
                EntidadeContextual.data_mencao.desc(),
                EntidadeContextual.id_entidade_contextual.desc()
            )
            .limit(
                limite
            )
        )


        resultado = db.execute(
            consulta
        )


        return list(
            resultado
            .scalars()
            .all()
        )


    # =========================================================
    # BUSCAR ENTIDADE EM FOCO
    # =========================================================

    @staticmethod
    def buscar_foco_atual(
        db: Session,
        id_usuario: int,
        id_conversa: int,
        tipo_entidade: str
    ) -> EntidadeContextual | None:

        resultado = db.execute(
            select(
                EntidadeContextual
            )
            .where(
                EntidadeContextual.id_usuario
                == id_usuario,

                EntidadeContextual.id_conversa
                == id_conversa,

                EntidadeContextual.tipo_entidade
                == tipo_entidade,

                EntidadeContextual.ordem_contexto
                == 1
            )
            .order_by(
                EntidadeContextual.data_mencao.desc(),
                EntidadeContextual.id_entidade_contextual.desc()
            )
            .limit(1)
        )


        return (
            resultado
            .scalars()
            .first()
        )


    # =========================================================
    # BUSCAR FOCO ANTERIOR
    # =========================================================

    @staticmethod
    def buscar_foco_anterior(
        db: Session,
        id_usuario: int,
        id_conversa: int,
        tipo_entidade: str
    ) -> EntidadeContextual | None:

        entidades = (
            EntidadeContextualRepository
            .listar_por_foco(
                db=db,
                id_usuario=id_usuario,
                id_conversa=id_conversa,
                tipo_entidade=tipo_entidade,
                limite=100
            )
        )


        # =====================================================
        # REMOVE DUPLICATAS DA MESMA ENTIDADE
        # =====================================================

        ids_encontrados = set()

        entidades_unicas = []


        for entidade in entidades:

            if (
                entidade.id_entidade
                in ids_encontrados
            ):
                continue

            ids_encontrados.add(
                entidade.id_entidade
            )

            entidades_unicas.append(
                entidade
            )


        if len(entidades_unicas) < 2:
            return None


        # posição 0 = atual
        # posição 1 = anterior
        return entidades_unicas[1]


    # =========================================================
    # DEFINIR UMA ENTIDADE COMO FOCO
    #
    # Pode ser útil quando o usuário disser:
    #
    # "volta para a tarefa de Java"
    #
    # sem necessariamente executar outra ação.
    # =========================================================

    @staticmethod
    def definir_foco(
        db: Session,
        id_usuario: int,
        id_conversa: int,
        tipo_entidade: str,
        id_entidade: int
    ) -> None:

        try:

            # Todos descem uma posição.

            db.execute(
                update(
                    EntidadeContextual
                )
                .where(
                    EntidadeContextual.id_usuario
                    == id_usuario,

                    EntidadeContextual.id_conversa
                    == id_conversa,

                    EntidadeContextual.tipo_entidade
                    == tipo_entidade
                )
                .values(
                    ordem_contexto=(
                        EntidadeContextual.ordem_contexto
                        + 1
                    )
                )
            )


            # A entidade escolhida volta para posição 1.

            db.execute(
                update(
                    EntidadeContextual
                )
                .where(
                    EntidadeContextual.id_usuario
                    == id_usuario,

                    EntidadeContextual.id_conversa
                    == id_conversa,

                    EntidadeContextual.tipo_entidade
                    == tipo_entidade,

                    EntidadeContextual.id_entidade
                    == id_entidade
                )
                .values(
                    ordem_contexto=1
                )
            )


            db.commit()


        except Exception:

            db.rollback()

            raise


    # =========================================================
    # LIMPAR CONTEXTO DA CONVERSA
    # =========================================================

    @staticmethod
    def limpar_conversa(
        db: Session,
        id_usuario: int,
        id_conversa: int
    ) -> None:

        try:

            db.execute(
                delete(
                    EntidadeContextual
                )
                .where(
                    EntidadeContextual.id_usuario
                    == id_usuario,

                    EntidadeContextual.id_conversa
                    == id_conversa
                )
            )

            db.commit()


        except Exception:

            db.rollback()

            raise