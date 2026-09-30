from sqlalchemy.orm import Session

from app.models.perfil_personalizacao import (
    PerfilPersonalizacao
)
from app.repositories.perfil_personalizacao_repository import (
    PerfilPersonalizacaoRepository
)
from app.schemas.perfil_personalizacao import (
    PerfilPersonalizacaoUpdate
)

class PerfilPersonalizacaoService:

    @staticmethod
    def obter(
            db: Session,
            id_usuario: int
    ) ->  PerfilPersonalizacao:

        return (
            PerfilPersonalizacaoRepository.obter_ou_criar(
                db=db,
                id_usuario=id_usuario
            )
        )

    @staticmethod
    def atualizar(
            db: Session,
            id_usuario: int,
            dados: PerfilPersonalizacaoUpdate
    ) -> PerfilPersonalizacao:
        perfil = (
            PerfilPersonalizacaoRepository
            .obter_ou_criar(
                db=db,
                id_usuario=id_usuario
            )
        )

        alteracoes = dados.model_dump(
            exclude_unset=True
        )

        for campo, valor in alteracoes.items():
            setattr(
                perfil,
                campo,
                valor
            )

        return (
            PerfilPersonalizacaoRepository
            .salvar(
                db=db,
                perfil=perfil
            )
        )