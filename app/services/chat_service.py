from app.services.consulta_instrucional_service import ConsultaInstrucionalService
from time import perf_counter

import re


from sqlalchemy.orm import Session


from app.services.instructional_query_handler_service import (
    InstructionalQueryHandlerService
)

from app.services.multi_intent_handler_service import (
    MultiIntentHandlerService
)



from app.conversation.response_policy import ResponsePolicy

from app.ai.capability_response_guard import (
    CapabilityResponseGuard
)

from app.services.memory_extraction_service import (
    MemoryExtractionService
)


from app.ai.operational_response_guard import (
    OperationalResponseGuard
)



from app.ai.prompt_builder import (
    PromptBuilder as AIPromptBuilder
)

from app.conversation.prompt_builder import (
    PromptBuilder as ConversationPromptBuilder
)


from app.services.time_service import (
    TimeService
)


from app.services.contexto_agente_service import (
    ContextoAgenteService
)


from app.ai.engine import ai_engine

from app.services.action_guard_service import ActionGuardService

from app.memory.memory_manager import MemoryManager

from app.models.mensagem import (
    Mensagem,
    RemetenteMensagem
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

from app.services.chat_interaction_service import (
    ChatInteractionService
)

from app.repositories.mensagem_repository import (
    MensagemRepository
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

        # =========================================================
        # ACTION GUARD — BARREIRA EXPLÍCITA
        # =========================================================

        resultado_guard = ActionGuardService.analisar(
            conteudo
        )

        # =========================================================
        # ACTION GUARD — BARREIRA CONTEXTUAL
        # =========================================================
        #
        # Este bloco só é alcançado depois que o Agent não
        # conseguiu executar uma Tool.
        #
        # O contexto serve somente para impedir que uma
        # solicitação operacional incompleta caia no modelo
        # conversacional e produza uma falsa confirmação.

        if not resultado_guard.operacional:

            dominio_contextual = None

            texto_guard = (
                ActionGuardService._normalizar(
                    conteudo
                )
            )

            # -----------------------------------------------------
            # CONTEXTO MAIS RECENTE
            # -----------------------------------------------------

            id_ultima_tarefa = (
                ContextoAgenteService
                .obter_ultima_tarefa_id(
                    db=db,
                    id_usuario=id_usuario,
                    id_conversa=id_conversa
                )
            )

            id_ultimo_lembrete = (
                ContextoAgenteService
                .obter_ultimo_lembrete_id(
                    db=db,
                    id_usuario=id_usuario,
                    id_conversa=id_conversa
                )
            )

            # -----------------------------------------------------
            # REFERÊNCIAS
            # -----------------------------------------------------

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

            # -----------------------------------------------------
            # RESOLUÇÃO CONSERVADORA DO DOMÍNIO
            # -----------------------------------------------------
            #
            # Um lembrete só é inferido quando a palavra
            # "lembrete" aparece explicitamente.
            #
            # Isso impede que "ela" seja associado a um
            # lembrete quando existe também uma tarefa em
            # contexto.

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


            # -----------------------------------------------------
            # SEGUNDA BARREIRA
            # -----------------------------------------------------

            resultado_guard = (
                ActionGuardService
                .analisar_contextual(
                    mensagem=conteudo,
                    dominio_contextual=dominio_contextual
                )
            )


        # =========================================================
        # BLOQUEIO DE OPERAÇÃO NÃO CONFIRMADA
        # =========================================================

        if resultado_guard.operacional:

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


        inicio_memoria = perf_counter()

        memorias = MemoryManager.buscar_relevantes(
            db=db,
            id_usuario=id_usuario,
            mensagem_atual=conteudo,
            limite=5
        )

        print(
            f"[PERFORMANCE] Busca memória: "
            f"{perf_counter() - inicio_memoria:.2f}s"
        )


        # =========================================================
        # 10. FLUXO NORMAL DE CONVERSA
        # =========================================================



        contexto_memoria = (
            MemoryManager.montar_contexto(
                memorias
            )
        )


        # =========================================================
        # 11. SALVA MENSAGEM DO USUÁRIO
        # =========================================================

        mensagem_usuario = Mensagem(
            id_conversa=id_conversa,
            remetente=RemetenteMensagem.USUARIO,
            conteudo=conteudo,
            tipo="TEXTO"
        )

        MensagemRepository.criar(
            db,
            mensagem_usuario
        )


        # =========================================================
        # 12. BUSCA HISTÓRICO
        # =========================================================

        historico = (
            MensagemRepository.listar_por_conversa(
                db,
                id_conversa
            )
        )

        historico = historico[-20:]

        contexto_temporal = (
            TimeService.contexto_temporal()
        )

        # POLÍTICA CONVERSACIONAL DA RESPOSTA ATUAL

        perfil_resposta = (
            ResponsePolicy.definir(
                conteudo
            )
        )

        politica_resposta = (
            ConversationPromptBuilder.construir_politica(perfil_resposta)
        )

        print(
            "[RESPONSE POLICY] "
            f"tamanho={perfil_resposta.tamanho.value} | "
            f"markdown={perfil_resposta.markdown.value} | "
            f"max_tokens={perfil_resposta.max_tokens} | "
            f"temperatura={perfil_resposta.temperatura}"
        )

        # PROMPT BUILDER

        mensagens_ia = AIPromptBuilder.montar_mensagens(
            contexto_temporal=contexto_temporal,
            contexto_memoria=contexto_memoria,
            historico=historico
        )

        # =========================================================
        # 16. EXECUTA A IA
        # =========================================================

        inicio = perf_counter()

        resultado_ia = ai_engine.gerar_resultado(
            mensagens_ia
        )

        resposta = resultado_ia.resposta

        print(
            "[AI RESULT] "
            f"provider={resultado_ia.provider} | "
            f"modelo={resultado_ia.modelo}"
        )

        if resposta is None or not str(resposta).strip():
            resposta = (
                "Não consegui gerar uma resposta adequada agora. "
                "Tente reformular sua solicitação."
            )

        resposta = str(resposta).strip()

        # =========================================================
        # OPERATIONAL RESPONSE GUARD
        # =========================================================

        resposta_original = resposta

        resposta = OperationalResponseGuard.validar(
            mensagem_usuario=conteudo,
            resposta_modelo=resposta
        )

        if resposta != resposta_original:
            print(
                "[OPERATIONAL RESPONSE GUARD] "
                "Falsa confirmação bloqueada."
            )

        resposta_antes_capability = resposta

        resposta = CapabilityResponseGuard.validar(
            mensagem_usuario=conteudo,
            resposta_modelo=resposta
        )

        if resposta != resposta_antes_capability:
            print("[CAPABILITY RESPONSE GUARD] "
                  "Capacidade inexistente bloqueada.")



        tempo = (
            perf_counter()
            - inicio
        )

        print(
            f"[PERFORMANCE] IA principal: "
            f"{perf_counter() - inicio:.2f}s"
        )


        # =========================================================
        # 17. SALVA RESPOSTA DA A.R.A.
        # =========================================================

        mensagem_ara = Mensagem(
            id_conversa=id_conversa,
            remetente=RemetenteMensagem.ARA,
            conteudo=resposta,
            tipo="TEXTO",
            modelo_ia=resultado_ia.modelo,
            tempo_processamento=tempo
        )


        MensagemRepository.criar(
            db,
            mensagem_ara
        )


        # =========================================================
        # 18. ATUALIZA A CONVERSA
        # =========================================================

        ConversaService.atualizar_atividade(
            db,
            id_conversa
        )


        # =========================================================
        # 19. EXTRAÇÃO DE MEMÓRIA
        # =========================================================
        MemoryExtractionService.processar(
            db=db,
            id_usuario=id_usuario,
            conteudo=conteudo
        )



        # =========================================================
        # 20. RETORNO NORMAL
        # =========================================================

        return {
            "id_conversa": id_conversa,
            "mensagem_usuario": conteudo,
            "resposta_ara": resposta,
            "provider": resultado_ia.provider,
            "modelo": resultado_ia.modelo,
            "ferramenta": None,
            "tempo_processamento": tempo,

        }
