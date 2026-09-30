from sqlalchemy.orm import Session

from app.services.chat_interaction_service import ChatInteractionService
from app.services.consulta_instrucional_service import ConsultaInstrucionalService


class InstructionalQueryHandlerService:

    @staticmethod
    def processar(
            db: Session,
            id_conversa: int,
            conteudo: str
    ) -> dict | None:

        consulta_instrucional = (
            ConsultaInstrucionalService.analisar(
                conteudo
            )
        )

        if consulta_instrucional is None:
            return None

        resposta = (
            consulta_instrucional[
                "resposta"
            ]
        )

        ChatInteractionService.salvar_agent(
            db=db,
            id_conversa=id_conversa,
            conteudo_usuario=conteudo,
            resposta_ara=resposta
        )

        return {
            "id_conversa": id_conversa,
            "mensagem_usuario": conteudo,
            "resposta_ara": resposta,
            "modelo": "AGENT",
            "ferramenta": None,
            "tempo_processamento": 0
        }