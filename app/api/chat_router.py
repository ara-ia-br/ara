from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.services.chat_service import ChatService
from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
    RecalcularRotaRequest,
    RecalcularRotaResponse
)

from app.agent.tools.route_tools import (
    consultar_rota
)

from app.ai.response_composer import (
    ResponseComposer
)

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
            db=db,
            id_conversa=dados.id_conversa,
            conteudo=dados.mensagem,
            localizacao=(
                dados.localizacao.model_dump()
                if dados.localizacao
                else None
            )
        )

    except ValueError as erro:
        raise HTTPException(
            status_code=404,
            detail=str(erro)
        )

@router.post(
    "/rota/recalcular",
    response_model=RecalcularRotaResponse
)
def recalcular_rota(
    dados: RecalcularRotaRequest
):

    resultado = consultar_rota(
        origem="daqui",
        destino=dados.destino,
        origem_latitude=dados.latitude,
        origem_longitude=dados.longitude
    )


    if resultado.get("sucesso") is False:

        raise HTTPException(
            status_code=400,
            detail=resultado.get(
                "erro",
                "Não consegui recalcular a rota."
            )
        )


    resposta = ResponseComposer.formatar_tool(
        "consultar_rota",
        resultado
    )


    return {
        "resposta_ara":
            resposta,

        "visualizacao":
            resultado.get(
                "visualizacao"
            )
    }