from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import ChatService


router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)


@router.post(
    "",
    response_model=ChatResponse
)
def chat(
    dados: ChatRequest,
    db: Session = Depends(get_db)
):
    try:
        return ChatService.enviar_mensagem(
            db,
            dados.id_conversa,
            dados.mensagem
        )

    except ValueError as erro:
        raise HTTPException(
            status_code=404,
            detail=str(erro)
        )