from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.arquivo import Arquivo


class ArquivoRepository:

    @staticmethod
    def criar(
        db: Session,
        arquivo: Arquivo
    ) -> Arquivo:

        db.add(
            arquivo
        )

        db.commit()

        db.refresh(
            arquivo
        )

        return arquivo


    @staticmethod
    def buscar_por_id(
        db: Session,
        id_arquivo: int
    ) -> Arquivo | None:

        return (
            db.execute(
                select(
                    Arquivo
                )
                .where(
                    Arquivo.id_arquivo
                    == id_arquivo
                )
            )
            .scalar_one_or_none()
        )


    @staticmethod
    def listar_por_usuario(
        db: Session,
        id_usuario: int
    ) -> list[Arquivo]:

        return list(
            db.execute(
                select(
                    Arquivo
                )
                .where(
                    Arquivo.id_usuario
                    == id_usuario
                )
                .order_by(
                    Arquivo.criado_em.desc()
                )
            )
            .scalars()
            .all()
        )


    @staticmethod
    def listar_por_conversa(
        db: Session,
        id_usuario: int,
        id_conversa: int
    ) -> list[Arquivo]:

        return list(
            db.execute(
                select(
                    Arquivo
                )
                .where(
                    Arquivo.id_usuario
                    == id_usuario,
                    Arquivo.id_conversa
                    == id_conversa
                )
                .order_by(
                    Arquivo.criado_em.desc()
                )
            )
            .scalars()
            .all()
        )


    @staticmethod
    def atualizar_status(
        db: Session,
        arquivo: Arquivo,
        status: str,
        erro_processamento: str | None = None
    ) -> Arquivo:

        arquivo.status = (
            status
        )

        arquivo.erro_processamento = (
            erro_processamento
        )

        db.commit()

        db.refresh(
            arquivo
        )

        return arquivo


    @staticmethod
    def salvar_texto_extraido(
        db: Session,
        arquivo: Arquivo,
        texto_extraido: str
    ) -> Arquivo:

        arquivo.texto_extraido = (
            texto_extraido
        )

        arquivo.status = (
            "PRONTO"
        )

        arquivo.erro_processamento = (
            None
        )

        db.commit()

        db.refresh(
            arquivo
        )

        return arquivo