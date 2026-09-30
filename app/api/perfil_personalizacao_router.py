from fastapi import (
    APIRouter,
    Depends
)
from sqlalchemy.orm import Session

from app.api import usuario_router
from app.database.connection import get_db
from app.models.usuario import Usuario
from app.schemas.perfil_personalizacao import (
    PerfilPersonalizacaoResponse,
    PerfilPersonalizacaoUpdate
)
from app.security.depedencies import (
    obter_usuario_atual
)
from app.services.perfil_personalizacao_service import (
    PerfilPersonalizacaoService
)

router = APIRouter(
    prefix="/perfil-personalizacao",
    tags=["Personalização"]
)

@router.get(
    "/me",
    response_model=PerfilPersonalizacaoResponse
)
def obter_meu_perfil(
    db: Session = Depends(get_db),
        usuario_atual: Usuario = Depends(
            obter_usuario_atual
        )
):
    return PerfilPersonalizacaoService.obter(
        db=db,
        id_usuario=usuario_atual.id_usuario
    )



@router.patch(
    "/me",
    response_model=PerfilPersonalizacaoResponse
)
def atualizar_meu_perfil(
        dados: PerfilPersonalizacaoUpdate,
        db: Session = Depends(get_db),
        usuario_atual: Usuario = Depends(
            obter_usuario_atual
        )
):
    return PerfilPersonalizacaoService.atualizar(
        db=db,
        id_usuario=usuario_atual.id_usuario,
        dados=dados
    )