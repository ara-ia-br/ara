from time import perf_counter

from sqlalchemy.orm import Session

from app.ai.capability_response_guard import (
    CapabilityResponseGuard
)

from app.ai.operational_response_guard import (
    OperationalResponseGuard
)

from app.conversation.perfil_persornalizacao_prompt_builder import (
    PersonalizationPromptBuilder
)
from app.models import perfil_personalizacao

from app.services.perfil_personalizacao_service import (
    PerfilPersonalizacaoService
)

from app.ai.prompt_builder import (
    PromptBuilder as AIPromptBuilder
)

from app.ai.engine import ai_engine

from app.conversation.response_policy import (
    ResponsePolicy
)

from app.conversation.prompt_builder import (
    PromptBuilder as ConversationPromptBuilder
)

from app.memory.memory_manager import (
    MemoryManager
)

from app.models.mensagem import (
    Mensagem,
    RemetenteMensagem
)

from app.repositories.mensagem_repository import (
    MensagemRepository
)

from app.services.conversa_service import (
    ConversaService
)

from app.services.memory_extraction_service import (
    MemoryExtractionService
)

from app.services.time_service import (
    TimeService
)


class ConversationalChatService:

    @staticmethod
    def processar(
        db: Session,
        id_usuario: int,
        id_conversa: int,
        conteudo: str
    ) -> dict:

        # =====================================================
        # MEMÓRIA RELEVANTE
        # =====================================================

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

        contexto_memoria = (
            MemoryManager.montar_contexto(
                memorias
            )
        )

        # =====================================================
        # SALVA MENSAGEM DO USUÁRIO
        # =====================================================

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

        # =====================================================
        # HISTÓRICO
        # =====================================================

        historico = (
            MensagemRepository.listar_por_conversa(
                db,
                id_conversa
            )
        )

        historico = historico[-20:]

        # =====================================================
        # CONTEXTO TEMPORAL
        # =====================================================

        contexto_temporal = (
            TimeService.contexto_temporal()
        )

        # ===================================================
        # PERSONALIZAÇÃO DO USUÁRIO
        # ===================================================

        perfil_personalizacao = (
            PerfilPersonalizacaoService.obter(
                db=db,
                id_usuario=id_usuario
            )
        )

        contexto_personalizacao = (
            PersonalizationPromptBuilder.construir(
                perfil_personalizacao
            )
        )

        print(
            "[PERSONALIZATION] "
            f"tom={perfil_personalizacao.tom} | "
            f"formalidade={perfil_personalizacao.formalidade} | "
            f"detalhe={perfil_personalizacao.nivel_detalhe} | "
            f"emojis={perfil_personalizacao.usar_emojis} | "
            f"estilo={perfil_personalizacao.estilo_resposta}"
        )



        # =====================================================
        # RESPONSE POLICY
        # =====================================================

        perfil_resposta = (
            ResponsePolicy.definir(
                conteudo
            )
        )

        # Mantido por compatibilidade com o fluxo atual.
        politica_resposta = (
            ConversationPromptBuilder
            .construir_politica(
                perfil_resposta
            )
        )

        print(
            "[RESPONSE POLICY] "
            f"tamanho={perfil_resposta.tamanho.value} | "
            f"markdown={perfil_resposta.markdown.value} | "
            f"max_tokens={perfil_resposta.max_tokens} | "
            f"temperatura={perfil_resposta.temperatura}"
        )

        # =====================================================
        # PROMPT BUILDER
        # =====================================================

        mensagens_ia = (
            AIPromptBuilder.montar_mensagens(
                contexto_temporal=contexto_temporal,
                contexto_memoria=contexto_memoria,
                historico=historico,
                contexto_personalizacao=contexto_personalizacao,
                politica_resposta=politica_resposta
            )
        )

        # =====================================================
        # EXECUTA IA
        # =====================================================

        inicio = perf_counter()

        resultado_ia = (
            ai_engine.gerar_resultado(
                mensagens_ia,
                temperatura=perfil_resposta.temperatura,
                max_tokens=perfil_resposta.max_tokens
            )
        )

        resposta = resultado_ia.resposta

        print(
            "[AI RESULT] "
            f"provider={resultado_ia.provider} | "
            f"modelo={resultado_ia.modelo}"
        )

        if (
            resposta is None
            or not str(resposta).strip()
        ):
            resposta = (
                "Não consegui gerar uma resposta adequada agora. "
                "Tente reformular sua solicitação."
            )

        resposta = str(resposta).strip()

        # =====================================================
        # OPERATIONAL RESPONSE GUARD
        # =====================================================

        resposta_original = resposta

        resposta = (
            OperationalResponseGuard.validar(
                mensagem_usuario=conteudo,
                resposta_modelo=resposta
            )
        )

        if resposta != resposta_original:
            print(
                "[OPERATIONAL RESPONSE GUARD] "
                "Falsa confirmação bloqueada."
            )

        # =====================================================
        # CAPABILITY RESPONSE GUARD
        # =====================================================

        resposta_antes_capability = resposta

        resposta = (
            CapabilityResponseGuard.validar(
                mensagem_usuario=conteudo,
                resposta_modelo=resposta
            )
        )

        if resposta != resposta_antes_capability:
            print(
                "[CAPABILITY RESPONSE GUARD] "
                "Capacidade inexistente bloqueada."
            )

        # =====================================================
        # TEMPO
        # =====================================================

        tempo = (
            perf_counter()
            - inicio
        )

        print(
            f"[PERFORMANCE] IA principal: "
            f"{tempo:.2f}s"
        )

        # =====================================================
        # SALVA RESPOSTA DA A.R.A.
        # =====================================================

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

        # =====================================================
        # ATUALIZA CONVERSA
        # =====================================================

        ConversaService.atualizar_atividade(
            db,
            id_conversa
        )

        # =====================================================
        # EXTRAÇÃO DE MEMÓRIA
        # =====================================================

        MemoryExtractionService.processar(
            db=db,
            id_usuario=id_usuario,
            conteudo=conteudo
        )

        # =====================================================
        # RETORNO
        # =====================================================

        return {
            "id_conversa": id_conversa,
            "mensagem_usuario": conteudo,
            "resposta_ara": resposta,
            "provider": resultado_ia.provider,
            "modelo": resultado_ia.modelo,
            "ferramenta": None,
            "tempo_processamento": tempo
        }