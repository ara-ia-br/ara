from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.schemas.usuario import UsuarioCreate, UsuarioResponse
from app.security.depedencies import obter_usuario_atual
from app.services.usuario_service import UsuarioService


router = APIRouter(
    prefix="/usuarios",
    tags=["Usuários"]
)


@router.post(
    "",
    response_model=UsuarioResponse,
    status_code=status.HTTP_201_CREATED
)
def criar_usuario(
    dados: UsuarioCreate,
    db: Session = Depends(get_db)
):
    try:
        return UsuarioService.criar(db, dados)

    except ValueError as erro:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(erro)
        )


# ESTA ROTA PRECISA VIR ANTES DE /{id_usuario}
@router.get(
    "/me",
    response_model=UsuarioResponse
)
def usuario_atual(
    usuario_atual=Depends(obter_usuario_atual)
):
    return usuario_atual


# ESTA ROTA PRECISA VIR DEPOIS
@router.get(
    "/{id_usuario}",
    response_model=UsuarioResponse
)
def buscar_usuario(
    id_usuario: int,
    db: Session = Depends(get_db)
):
    usuario = UsuarioService.buscar_por_id(
        db,
        id_usuario
    )

    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado."
        )

    return usuario