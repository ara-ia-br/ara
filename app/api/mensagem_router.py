from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.schemas.mensagem import (
    MensagemCreate,
    MensagemResponse
)
from app.services.mensagem_service import MensagemService


router = APIRouter(
    prefix="/mensagens",
    tags=["Mensagens"]
)


@router.post(
    "",
    response_model=MensagemResponse,
    status_code=status.HTTP_201_CREATED
)
def criar_mensagem(
    dados: MensagemCreate,
    db: Session = Depends(get_db)
):

    try:
        return MensagemService.criar(
            db,
            dados
        )

    except ValueError as erro:
        raise HTTPException(
            status_code=404,
            detail=str(erro)
        )


@router.get(
    "/conversa/{id_conversa}",
    response_model=list[MensagemResponse]
)
def listar_mensagens_conversa(
    id_conversa: int,
    db: Session = Depends(get_db)
):
    return MensagemService.listar_por_conversa(
        db,
        id_conversa
    )