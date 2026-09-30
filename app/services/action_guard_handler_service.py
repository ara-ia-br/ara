import re

from sqlalchemy.orm import Session

from app.services.action_guard_service import ActionGuardService
from app.services.chat_interaction_service import ChatInteractionService
from app.services.contexto_agente_service import ContextoAgenteService


class ActionGuardHandlerService:

    @staticmethod
    def processar(
            db: Session,
            id_usuario: int,
            id_conversa: int,
            conteudo: str
    ) -> dict | None:

        # BARREIRA EXPLÍCITA
        resultado_guard = (
            ActionGuardService.analisar(conteudo)
        )


        # BARREIRA CONTEXTUAL
        if not resultado_guard.operacional:
            dominio_contextual = None

            texto_guard = (
                ActionGuardService._normalizar(conteudo)
            )

            id_ultima_tarefa = (
                ContextoAgenteService.obter_ultima_tarefa_id(
                    db=db,
                    id_usuario=id_usuario,
                    id_conversa=id_conversa,
                )
            )

            id_ultimo_lembrete = (
                ContextoAgenteService.obter_ultimo_lembrete_id(
                    db=db,
                    id_usuario=id_usuario,
                    id_conversa=id_conversa
                )
            )

            referencia_lembrete = bool(
                re.search(
                    r"\blembretes?\b",
                    texto_guard
                )
            )

            referencia_tarefa = bool(
                re.search(
                    r"\b(?:"
                    r"ela"
                    r"|dela"
                    r"|essa"
                    r"|dessa"
                    r"|esta"
                    r"|desta"
                    r"|tarefas?"
                    r"|prioridade"
                    r")\b",
                    texto_guard
                )
            )

            if (
                referencia_lembrete
                and id_ultimo_lembrete is not None
            ):
                dominio_contextual = "LEMBRETE"

            elif (
                referencia_tarefa
                and id_ultima_tarefa is not None
            ):
                dominio_contextual = "TAREFA"

            resultado_guard = (
                ActionGuardService.analisar_contextual(
                    mensagem=conteudo,
                    dominio_contextual=dominio_contextual
                )
            )


            # NÃO HÁ BLOQUEIO

            if not resultado_guard.operacional:
                return None


            # BLOQUEIO

            resposta = (
                resultado_guard.resposta
                or (
                "Entendi que você quer executar uma ação, "
                "mas não consegui confirmá-la com segurança."
                )
            )

            print(
                "[ACTION GUARD] "
                f"bloqueado | "
                f"dominio={resultado_guard.dominio} | "
                f"operacao={resultado_guard.operacao}"
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
                "modelo": "ACTION_GUARD",
                "ferramenta": None,
                "tempo_processamento": 0
            }