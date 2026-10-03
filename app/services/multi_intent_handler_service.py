from time import perf_counter

from sqlalchemy.orm import Session

from app.agent.agent import AraAgent
from app.agent.intent import TipoAcao
from app.agent.tool_registry import ToolRegistry
from app.agent.plan_executor import AgentPlanExecutor

from app.ai.response_composer import ResponseComposer

from app.services.confirmation_policy_service import (
    ConfirmationPolicyService
)

from app.services.contexto_agente_service import (
    ContextoAgenteService
)

from app.services.entidade_contextual_service import (
    EntidadeContextualService
)

from app.services.chat_interaction_service import (
    ChatInteractionService
)

from app.services.memory_extraction_service import (
    MemoryExtractionService
)

from app.services.title_cleaner_service import (
    TitleCleanerService
)
from app.services.weather_context_service import WeatherContextService


class MultiIntentHandlerService:

    @staticmethod
    def processar(
        db: Session,
        id_usuario: int,
        id_conversa: int,
        conteudo: str
    ) -> dict | None:

        inicio_agent = perf_counter()

        # =====================================================
        # CONTEXTO NATIVO DE CLIMA
        # =====================================================

        decisao_contextual = (
            WeatherContextService.analisar(
                mensagem=conteudo,
                db=db,
                id_conversa=id_conversa
            )
        )


        plano = None

        if decisao_contextual is None:

            plano = AraAgent.planejar(
                mensagem=conteudo,
                db=db,
                id_usuario=id_usuario,
                id_conversa=id_conversa
            )

        if plano is None:
            return None

        # =====================================================
        # PRÉ-VALIDAÇÃO DO PLANO
        # =====================================================

        for passo in plano.passos:

            decisao_passo = passo.decisao
            ferramenta_passo = decisao_passo.ferramenta

            if (
                decisao_passo.acao != TipoAcao.EXECUTAR
                or ferramenta_passo is None
            ):

                resposta = (
                    "Não consegui montar todas as ações "
                    "desse pedido com segurança."
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

            if not ToolRegistry.existe(
                ferramenta_passo
            ):

                resposta = (
                    f"A ferramenta '{ferramenta_passo}' "
                    "não está disponível no momento."
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

            argumentos_pre_validacao = (
                decisao_passo.argumentos.copy()
                if decisao_passo.argumentos
                else {}
            )

            dados_confirmacao = (
                ConfirmationPolicyService.preparar(
                    ferramenta=ferramenta_passo,
                    argumentos=argumentos_pre_validacao
                )
            )

            if dados_confirmacao is not None:

                resposta = (
                    "Esse pedido contém várias ações e uma delas "
                    "precisa de confirmação. Por segurança, nenhuma "
                    "ação foi executada."
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

        # =====================================================
        # EXECUTOR SEGURO DAS ETAPAS
        # =====================================================

        def executar_passo_plano(
            decisao_passo,
            argumentos_passo
        ):

            ferramenta = decisao_passo.ferramenta

            if not ferramenta:
                raise ValueError(
                    "Etapa do plano sem ferramenta definida."
                )

            if not ToolRegistry.existe(
                ferramenta
            ):
                raise ValueError(
                    f"Ferramenta '{ferramenta}' não encontrada."
                )

            argumentos = (
                argumentos_passo.copy()
                if argumentos_passo
                else {}
            )

            # =================================================
            # CONFIRMAÇÃO APÓS RESOLUÇÃO DOS ARGUMENTOS
            # =================================================

            dados_confirmacao = (
                ConfirmationPolicyService.preparar(
                    ferramenta=ferramenta,
                    argumentos=argumentos
                )
            )

            if dados_confirmacao is not None:
                raise ValueError(
                    "Uma etapa do plano exige confirmação "
                    "antes de ser executada."
                )

            # =================================================
            # DADOS INTERNOS
            # =================================================

            argumentos["db"] = db
            argumentos["id_usuario"] = id_usuario

            # =================================================
            # LIMPEZA DO TÍTULO
            # =================================================

            if (
                "titulo" in argumentos
                and isinstance(
                    argumentos["titulo"],
                    str
                )
            ):

                argumentos["titulo"] = (
                    TitleCleanerService.limpar(
                        argumentos["titulo"]
                    )
                )

            # =================================================
            # EXECUTA TOOL
            # =================================================

            resultado = ToolRegistry.executar(
                ferramenta,
                **argumentos
            )

            if not isinstance(
                resultado,
                dict
            ):
                raise ValueError(
                    "A ferramenta não retornou "
                    "um resultado válido."
                )

            if resultado.get(
                "sucesso"
            ) is False:
                raise ValueError(
                    resultado.get(
                        "erro",
                        "A operação não foi concluída."
                    )
                )

            # =================================================
            # CONTEXTO DE TAREFA
            # =================================================

            id_tarefa_resultado = (
                resultado.get(
                    "id_tarefa"
                )
            )

            if (
                id_tarefa_resultado is not None
                and "tarefa" in ferramenta
            ):

                titulo_tarefa_resultado = (
                    resultado.get(
                        "titulo"
                    )
                )

                ContextoAgenteService.registrar_tarefa(
                    db=db,
                    id_usuario=id_usuario,
                    id_conversa=id_conversa,
                    id_tarefa=id_tarefa_resultado,
                    ferramenta=ferramenta
                )

                EntidadeContextualService.registrar(
                    db=db,
                    id_usuario=id_usuario,
                    id_conversa=id_conversa,
                    tipo_entidade="TAREFA",
                    id_entidade=id_tarefa_resultado,
                    titulo=titulo_tarefa_resultado
                )

            # =================================================
            # CONTEXTO DE LEMBRETE
            # =================================================

            id_lembrete_resultado = (
                resultado.get(
                    "id_lembrete"
                )
            )

            if (
                id_lembrete_resultado is not None
                and "lembrete" in ferramenta
            ):

                ContextoAgenteService.registrar_lembrete(
                    db=db,
                    id_usuario=id_usuario,
                    id_conversa=id_conversa,
                    id_lembrete=id_lembrete_resultado,
                    ferramenta=ferramenta
                )

                EntidadeContextualService.registrar(
                    db=db,
                    id_usuario=id_usuario,
                    id_conversa=id_conversa,
                    tipo_entidade="LEMBRETE",
                    id_entidade=id_lembrete_resultado,
                    titulo=resultado.get(
                        "titulo"
                    )
                )

            return resultado

        # =====================================================
        # EXECUTAR PLANO
        # =====================================================

        try:

            resultados_planos = (
                AgentPlanExecutor.executar(
                    plano=plano,
                    executar_passo=executar_passo_plano
                )
            )

        except ValueError as erro:

            resposta = str(erro)

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

        except TypeError as erro:

            print(
                f"Erro de argumentos no plano: {erro}"
            )

            resposta = (
                "Eita! Faltou uma informação para eu executar "
                "todas as ações desse pedido."
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

        # =====================================================
        # MONTA RESPOSTA ÚNICA
        # =====================================================

        resposta_plano = []

        for passo, resultado in zip(
            plano.passos,
            resultados_planos
        ):

            ferramenta = (
                passo.decisao.ferramenta
            )

            if ferramenta is None:
                continue

            resposta_etapa = (
                ResponseComposer.formatar_tool(
                    ferramenta,
                    resultado
                )
            )

            if resposta_etapa:
                resposta_plano.append(
                    resposta_etapa
                )

        if not resposta_plano:

            resposta = (
                "As ações foram processadas, "
                "mas não houve resposta para exibir."
            )

        else:

            resposta = "\n\n".join(
                resposta_plano
            )

        # =====================================================
        # PERSISTÊNCIA
        # =====================================================

        ChatInteractionService.salvar_agent(
            db=db,
            id_conversa=id_conversa,
            conteudo_usuario=conteudo,
            resposta_ara=resposta
        )

        # =====================================================
        # MEMÓRIA
        # =====================================================

        MemoryExtractionService.processar(
            db=db,
            id_usuario=id_usuario,
            conteudo=conteudo
        )

        print(
            f"[PERFORMANCE] Agent Plan: "
            f"{perf_counter() - inicio_agent:.2f}s"
        )

        return {
            "id_conversa": id_conversa,
            "mensagem_usuario": conteudo,
            "resposta_ara": resposta,
            "modelo": "AGENT",
            "ferramenta": "MULTI_INTENT",
            "tempo_processamento": 0
        }