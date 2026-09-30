from sqlalchemy.orm import Session

from app.services.instructional_query_handler_service import (
    InstructionalQueryHandlerService
)

from app.services.conversational_chat_service import (
    ConversationalChatService
)

from app.services.multi_intent_handler_service import (
    MultiIntentHandlerService
)

from app.services.action_guard_handler_service import (
    ActionGuardHandlerService
)

from app.repositories.conversa_repository import (
    ConversaRepository
)

from app.services.agent_action_handler_service import (
    AgentActionHandlerService
)

from app.services.pending_action_handler_service import (
    PendingActionHandlerService
)

from app.services.conversa_service import (
    ConversaService
)

class ChatService:
    # =========================================================
    # MÉTODO PRINCIPAL
    # =========================================================

    @staticmethod
    def enviar_mensagem(
        db: Session,
        id_conversa: int,
        conteudo: str
    ) -> dict:

        # =====================================================
        # 1. BUSCA A CONVERSA
        # =====================================================

        conversa = ConversaRepository.buscar_por_id(
            db,
            id_conversa
        )

        if conversa is None:

            raise ValueError(
                "Conversa não encontrada."
            )


        # =====================================================
        # 2. IDENTIFICA O USUÁRIO
        # =====================================================

        id_usuario = conversa.id_usuario


        # =====================================================
        # 3. GERA TÍTULO AUTOMÁTICO DA CONVERSA
        # =====================================================

        ConversaService.gerar_titulo_automatico(
            db=db,
            id_conversa=id_conversa,
            primeira_mensagem=conteudo
        )

        # =====================================================
        # CONFIRMAÇÃO DE AÇÃO PENDENTE
        # =====================================================

        resultado_acao_pendente = (
            PendingActionHandlerService.processar(
                db=db,
                id_usuario=id_usuario,
                id_conversa=id_conversa,
                conteudo=conteudo
            )
        )

        if resultado_acao_pendente is not None:
            return resultado_acao_pendente

        # =====================================================
        # CONSULTA INSTRUCIONAL OPERACIONAL
        # =====================================================

        resultado_instrucional = (
            InstructionalQueryHandlerService.processar(
                db=db,
                id_conversa=id_conversa,
                conteudo=conteudo
            )
        )

        if resultado_instrucional is not None:
              return resultado_instrucional



        # SPRINT 9

        resultado_multi_intent = (
            MultiIntentHandlerService.processar(
                db=db,
                id_usuario=id_usuario,
                id_conversa=id_conversa,
                conteudo=conteudo
            )
        )

        if resultado_multi_intent is not None:
            return resultado_multi_intent


        resultado_agent = (
            AgentActionHandlerService.processar(
                db=db,
                id_usuario=id_usuario,
                id_conversa=id_conversa,
                conteudo=conteudo
            )
       )

        if resultado_agent is not None:
            return resultado_agent


        resultado_action_guard = (
            ActionGuardHandlerService.processar(
                db=db,
                id_usuario=id_usuario,
                id_conversa=id_conversa,
                conteudo=conteudo
            )
        )

        if resultado_action_guard is not None:
            return resultado_action_guard


        return ConversationalChatService.processar(
            db=db,
            id_usuario=id_usuario,
            id_conversa=id_conversa,
            conteudo=conteudo
        )
