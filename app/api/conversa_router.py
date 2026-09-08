from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Response,
    status
)
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.schemas.conversa import (
    ConversaCreate,
    ConversaResponse,
    ConversaUpdateTitulo
)
from app.services.conversa_service import ConversaService


router = APIRouter(
    prefix="/conversas",
    tags=["Conversas"]
)


@router.post(
    "",
    response_model=ConversaResponse,
    status_code=status.HTTP_201_CREATED
)
def criar_conversa(
    dados: ConversaCreate,
    db: Session = Depends(get_db)
):
    try:
        return ConversaService.criar(
            db,
            dados
        )

    except ValueError as erro:
        raise HTTPException(
            status_code=404,
            detail=str(erro)
        )


@router.get(
    "/usuario/{id_usuario}",
    response_model=list[ConversaResponse]
)
def listar_conversas_usuario(
    id_usuario: int,
    db: Session = Depends(get_db)
):
    return ConversaService.listar_por_usuario(
        db,
        id_usuario
    )


@router.patch(
    "/{id_conversa}/titulo",
    response_model=ConversaResponse
)
def renomear_conversa(
    id_conversa: int,
    dados: ConversaUpdateTitulo,
    db: Session = Depends(get_db)
):
    try:
        return ConversaService.renomear(
            db,
            id_conversa,
            dados.titulo
        )

    except ValueError as erro:
        raise HTTPException(
            status_code=404,
            detail=str(erro)
        )


@router.patch(
    "/{id_conversa}/arquivar",
    response_model=ConversaResponse
)
def arquivar_conversa(
    id_conversa: int,
    db: Session = Depends(get_db)
):
    try:
        return ConversaService.arquivar(
            db,
            id_conversa
        )

    except ValueError as erro:
        raise HTTPException(
            status_code=404,
            detail=str(erro)
        )


@router.delete(
    "/{id_conversa}",
    status_code=status.HTTP_204_NO_CONTENT
)
def excluir_conversa(
    id_conversa: int,
    db: Session = Depends(get_db)
):
    try:
        ConversaService.excluir(
            db,
            id_conversa
        )

        return Response(
            status_code=status.HTTP_204_NO_CONTENT
        )

    except ValueError as erro:
        raise HTTPException(
            status_code=404,
            detail=str(erro)
        )



@router.get(
    "/usuario/{id_usuario}/arquivadas",
    response_model=list[ConversaResponse]
)
def listar_conversas_arquivadas(
    id_usuario: int,
    db: Session = Depends(get_db)
):
    return ConversaService.listar_arquivadas_por_usuario(
        db,
        id_usuario
    )


@router.patch(
    "/{id_conversa}/restaurar",
    response_model=ConversaResponse
)
def restaurar_conversa(
    id_conversa: int,
    db: Session = Depends(get_db)
):
    try:
        return ConversaService.restaurar(
            db,
            id_conversa
        )

    except ValueError as erro:
        raise HTTPException(
            status_code=404,
            detail=str(erro)
        )