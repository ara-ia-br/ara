from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.perfil_personalizacao import PerfilPersonalizacao


class PerfilPersonalizacaoRepository:

    @staticmethod
    def criar(
            db: Session,
            perfil: PerfilPersonalizacao
    ) -> PerfilPersonalizacao:

        db.add(perfil)
        db.commit()
        db.refresh(perfil)

        return perfil

    @staticmethod
    def buscar_por_id(
            db: Session,
            id_perfil: int
    ) -> PerfilPersonalizacao | None:

        return db.get(
            PerfilPersonalizacao,
            id_perfil
        )

    @staticmethod
    def buscar_por_usuario(
            db: Session,
            id_usuario: int
    ) -> PerfilPersonalizacao | None:

        resultado = db.execute(
            select(
                PerfilPersonalizacao
            ).where(
                PerfilPersonalizacao.id_usuario == id_usuario
            )
        )

        return resultado.scalar_one_or_none()

    @staticmethod
    def obter_ou_criar(
            db: Session,
            id_usuario: int
    ) -> PerfilPersonalizacao:

        perfil = (
            PerfilPersonalizacaoRepository.buscar_por_usuario(
                db, id_usuario
            )
        )

        if perfil is not None:
            return perfil

        perfil = PerfilPersonalizacao(id_usuario=id_usuario)

        return (
            PerfilPersonalizacaoRepository.criar(
                db, perfil
            )
        )

    @staticmethod
    def salvar(
            db: Session,
            perfil: PerfilPersonalizacao
    ) -> PerfilPersonalizacao:

        db.add(perfil)
        db.commit()
        db.refresh(perfil)

        return perfil

    @staticmethod
    def excluir(
            db: Session,
            perfil: PerfilPersonalizacao
    ) -> None:
        db.delete(perfil)
        db.commit()