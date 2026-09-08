from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.schemas.memoria import (
    MemoriaCreate,
    MemoriaResponse,
)
from app.services.memoria_service import MemoriaService


router = APIRouter(
    prefix="/memorias",
    tags=["Memórias"]
)


@router.post(
    "",
    response_model=MemoriaResponse,
    status_code=status.HTTP_201_CREATED
)
def criar_memoria(
    dados: MemoriaCreate,
    db: Session = Depends(get_db)
):
    try:
        return MemoriaService.criar(
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
    response_model=list[MemoriaResponse]
)
def listar_memorias(
    id_usuario: int,
    db: Session = Depends(get_db)
):
    return MemoriaService.listar_usuario(
        db,
        id_usuario
    )


@router.delete(
    "/{id_memoria}",
    response_model=MemoriaResponse
)
def desativar_memoria(
    id_memoria: int,
    db: Session = Depends(get_db)
):
    try:
        return MemoriaService.desativar(
            db,
            id_memoria
        )

    except ValueError as erro:
        raise HTTPException(
            status_code=404,
            detail=str(erro)
        )