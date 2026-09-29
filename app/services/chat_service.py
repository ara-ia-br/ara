from app.services.consulta_instrucional_service import ConsultaInstrucionalService
from app.services.confirmation_policy_service import ConfirmationPolicyService

from time import perf_counter

import re


from sqlalchemy.orm import Session





from app.conversation.response_policy import ResponsePolicy

from app.ai.capability_response_guard import (
    CapabilityResponseGuard
)




from app.ai.operational_response_guard import (
    OperationalResponseGuard
)

from app.ai.response_composer import ResponseComposer

from app.ai.prompt_builder import (
    PromptBuilder as AIPromptBuilder
)

from app.conversation.prompt_builder import (
    PromptBuilder as ConversationPromptBuilder
)


from app.services.time_service import (
    TimeService
)

from app.services.entidade_contextual_service import (
    EntidadeContextualService
)

from app.services.contexto_agente_service import (
    ContextoAgenteService
)

from app.services.acao_pendente_service import (
    AcaoPendenteService
)

from app.ai.engine import ai_engine

from app.agent.agent import AraAgent
from app.agent.intent import TipoAcao
from app.agent.tool_registry import ToolRegistry
from app.agent.plan_executor import AgentPlanExecutor
from app.services.action_guard_service import ActionGuardService

from app.memory.memory_extractor import MemoryExtractor
from app.memory.memory_manager import MemoryManager

from app.models.mensagem import (
    Mensagem,
    RemetenteMensagem
)

from app.repositories.conversa_repository import (
    ConversaRepository
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
    # EXTRAÇÃO DE MEMÓRIA
    # =========================================================

    @staticmethod
    def _extrair_memoria(
            db: Session,
            id_usuario: int,
            conteudo: str
    ) -> None:

        try:

            inicio_extracao = perf_counter()

            MemoryExtractor.processar(
                db=db,
                id_usuario=id_usuario,
                mensagem=conteudo
            )

            print(
                f"[PERFORMANCE] Extração memória: "
                f"{perf_counter() - inicio_extracao:.2f}s"
            )

        except Exception as erro:

            print(
                f"Erro ao extrair memória: {erro}"
            )

    # =========================================================
    # LIMPAR TÍTULOS DO AGENT
    # =========================================================

    @staticmethod
    def _limpar_titulo(
        texto: str
    ) -> str:

        texto = re.sub(
            r"\bprioridade\s+(máxima|maxima|alta|baixa|muito baixa|[1-5])\b",
            "",
            texto,
            flags=re.IGNORECASE
        )

        texto = re.sub(
            r"\b(urgente|urgentemente|muito urgente)\b",
            "",
            texto,
            flags=re.IGNORECASE
        )

        texto = re.sub(
            r"\s+",
            " ",
            texto
        )

        texto = texto.strip(
            " ,.-"
        )

        texto = re.sub(
            r"^para\s+",
            "",
            texto,
            flags=re.IGNORECASE
        )

        if not texto:
            return texto

        texto = texto.strip()

        texto = re.sub(
            r"""
            [,\s]*
            (
                por\s+favor
                |
                por\s+gentileza
                |
                pfv
                |
                pra\s+mim
                |
                para\s+mim
                |
                obrigado
                |
                obrigada
                |
                obg
                |
                beleza
                |
                blz
            )
            [.!?]*$
            """,
            "",
            texto,
            flags=(
                re.IGNORECASE
                | re.VERBOSE
            )
        )

        texto = texto.strip(
            " ,.!?;:-"
        )

        return texto


    # =========================================================
    # FORMATAR RESPOSTA DAS TOOLS
    # =========================================================




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

        texto_normalizado = (
            conteudo
            .strip()
            .lower()
        )

        texto_normalizado = re.sub(
            r"[.!?,;:]+$",
            "",
            texto_normalizado
        ).strip()

        confirmacoes = {
            "sim",
            "s",
            "confirmo",
            "confirmar",
            "pode",
            "pode sim",
            "sim pode",
            "sim, pode",
            "pode fazer",
            "pode excluir",
            "confirmo sim",
            "confirmo pode excluir",
            "tenho certeza"
        }

        recusas = {
            "não",
            "nao",
            "n",
            "cancelar",
            "cancela",
            "cancele",
            "não quero",
            "nao quero",
            "deixa",
            "deixa pra lá",
            "deixa pra la",
            "não faça",
            "nao faca"
        }

        acao_pendente = AcaoPendenteService.obter(
            id_usuario=id_usuario,
            id_conversa=id_conversa
        )

        # -----------------------------------------------------
        # USUÁRIO RECUSOU
        # -----------------------------------------------------

        if (
            acao_pendente is not None
            and texto_normalizado in recusas
        ):

            AcaoPendenteService.cancelar(
                id_usuario=id_usuario,
                id_conversa=id_conversa
            )

            resposta = (
                acao_pendente.get(
                    "mensagem_cancelamento"
                )
                or (
                    "Certo, ação cancelada. "
                    "Nada foi alterado."
                )
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

        # -----------------------------------------------------
        # USUÁRIO CONFIRMOU
        # -----------------------------------------------------

        if (
            acao_pendente is not None
            and texto_normalizado in confirmacoes
        ):

            acao = AcaoPendenteService.consumir(
                id_usuario=id_usuario,
                id_conversa=id_conversa
            )

            ferramenta = acao["ferramenta"]

            argumentos = dict(
                acao.get(
                    "argumentos",
                    {}
                )
            )

            argumentos["db"] = db
            argumentos["id_usuario"] = id_usuario

            try:

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
                ) is not True:
                    raise ValueError(
                        resultado.get(
                            "erro",
                            "A operação não foi concluída."
                        )
                    )

                resposta = (
                    ResponseComposer.formatar_tool(
                        ferramenta,
                        resultado
                    )
                )

            except Exception as erro:

                print(
                    "[AÇÃO PENDENTE] "
                    f"Falha em {ferramenta}: {erro}"
                )

                resposta = (
                    "Não consegui executar essa ação. "
                    "Nenhum sucesso foi confirmado."
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
                    "ferramenta": ferramenta,
                    "tempo_processamento": 0
                }

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
                "ferramenta": ferramenta,
                "tempo_processamento": 0
            }

        # =====================================================
        # CONSULTA INSTRUCIONAL OPERACIONAL
        # =====================================================

        consulta_instrucional = (
            ConsultaInstrucionalService.analisar(
                conteudo
            )
        )

        if consulta_instrucional is not None:

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

        inicio_agent = perf_counter()


        # =====================================================
        # SPRINT 9 - PLANEJAMENTO MULTI-INTENT
        # =====================================================

        plano = AraAgent.planejar(
            mensagem=conteudo,
            db=db,
            id_usuario=id_usuario,
            id_conversa=id_conversa
        )

        if plano is not None:

            # =================================================
            # PRÉ-VALIDAÇÃO DO PLANO
            # =================================================
            #
            # Nenhuma etapa é executada antes de validarmos
            # todas as ações conhecidas do plano. Isso evita
            # execução parcial quando uma etapa posterior exige
            # confirmação.
            # =================================================

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

                if not ToolRegistry.existe(ferramenta_passo):
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

            # =================================================
            # EXECUTOR SEGURO DAS ETAPAS DO PLANO
            # =================================================

            def executar_passo_plano(
                decisao_passo,
                argumentos_passo
            ):
                ferramenta = decisao_passo.ferramenta

                if not ferramenta:
                    raise ValueError(
                        "Etapa do plano sem ferramenta definida."
                    )

                if not ToolRegistry.existe(ferramenta):
                    raise ValueError(
                        f"Ferramenta '{ferramenta}' não encontrada."
                    )

                argumentos = (
                    argumentos_passo.copy()
                    if argumentos_passo
                    else {}
                )

                # ---------------------------------------------
                # CONFIRMATION POLICY APÓS RESOLVER ARGUMENTOS
                # ---------------------------------------------

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

                # ---------------------------------------------
                # DADOS INTERNOS
                # ---------------------------------------------

                argumentos["db"] = db
                argumentos["id_usuario"] = id_usuario

                # ---------------------------------------------
                # LIMPEZA DE TÍTULO
                # ---------------------------------------------

                if (
                    "titulo" in argumentos
                    and isinstance(argumentos["titulo"], str)
                ):
                    argumentos["titulo"] = (
                        ChatService._limpar_titulo(
                            argumentos["titulo"]
                        )
                    )

                # ---------------------------------------------
                # EXECUTA TOOL
                # ---------------------------------------------

                resultado = ToolRegistry.executar(
                    ferramenta,
                    **argumentos
                )

                if not isinstance(resultado, dict):
                    raise ValueError(
                        "A ferramenta não retornou "
                        "um resultado válido."
                    )

                if resultado.get("sucesso") is False:
                    raise ValueError(
                        resultado.get(
                            "erro",
                            "A operação não foi concluída."
                        )
                    )

                # ---------------------------------------------
                # CONTEXTO DE TAREFA
                # ---------------------------------------------

                id_tarefa_resultado = resultado.get(
                    "id_tarefa"
                )

                if (
                    id_tarefa_resultado is not None
                    and "tarefa" in ferramenta
                ):
                    titulo_tarefa_resultado = resultado.get(
                        "titulo"
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

                # ---------------------------------------------
                # CONTEXTO DE LEMBRETE
                # ---------------------------------------------

                id_lembrete_resultado = resultado.get(
                    "id_lembrete"
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
                        titulo=resultado.get("titulo")
                    )

                return resultado

            # =================================================
            # EXECUTAR PLANO MULTI-INTENT
            # =================================================

            try:
                resultados_planos = AgentPlanExecutor.executar(
                    plano=plano,
                    executar_passo=executar_passo_plano
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

            # =================================================
            # MONTA UMA ÚNICA RESPOSTA MULTI-INTENT
            # =================================================

            resposta_plano = []

            for passo, resultado in zip(
                plano.passos,
                resultados_planos
            ):
                ferramenta = passo.decisao.ferramenta

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

            # =================================================
            # SALVA INTERAÇÃO UMA ÚNICA VEZ
            # =================================================

            ChatInteractionService.salvar_agent(
                db=db,
                id_conversa=id_conversa,
                conteudo_usuario=conteudo,
                resposta_ara=resposta
            )

            # =================================================
            # MEMÓRIA
            # =================================================

            ChatService._extrair_memoria(
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

        # =====================================================
        # FLUXO TRADICIONAL DO AGENT
        # =====================================================

        decisao = AraAgent.decidir(
            mensagem=conteudo,
            db=db,
            id_usuario=id_usuario,
            id_conversa=id_conversa
        )

        print(
            f"[PERFORMANCE] Agent: "
            f"{perf_counter() - inicio_agent:.2f}s"
        )




        # =====================================================
        # 4. AGENT
        # =====================================================

        # =====================================================
        # 5. EXECUTAR TOOL
        # =====================================================

        if decisao.acao == TipoAcao.EXECUTAR:

            argumentos = (
                decisao.argumentos.copy()
                if decisao.argumentos
                else {}
            )

            # =================================================
            # CONFIRMATION POLICY — BARREIRA CENTRAL
            # =================================================
            #
            # Antes de qualquer Tool ser executada, verificamos
            # se a política central exige confirmação.
            #
            # Dados internos como db e id_usuario NÃO entram na
            # ação pendente. Eles serão injetados somente depois
            # que o usuário confirmar.
            # =================================================

            dados_confirmacao = (
                ConfirmationPolicyService.preparar(
                    ferramenta=decisao.ferramenta,
                    argumentos=argumentos
                )
            )

            if dados_confirmacao is not None:

                AcaoPendenteService.registrar(
                    id_usuario=id_usuario,
                    id_conversa=id_conversa,
                    ferramenta=
                        dados_confirmacao["ferramenta"],
                    argumentos=
                        dados_confirmacao["argumentos"],
                    dominio=
                        dados_confirmacao["dominio"],
                    operacao=
                        dados_confirmacao["operacao"],
                    descricao=
                        dados_confirmacao["descricao"],
                    mensagem_confirmacao=
                        dados_confirmacao[
                            "mensagem_confirmacao"
                        ],
                    mensagem_cancelamento=
                        dados_confirmacao[
                            "mensagem_cancelamento"
                        ]
                )

                resposta = (
                    dados_confirmacao[
                        "mensagem_confirmacao"
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


            # O backend injeta esses dados.
            # Nunca devem depender da IA.
            argumentos["db"] = db
            argumentos["id_usuario"] = id_usuario


            try:

                # =================================================
                # LIMPA TÍTULO
                # =================================================

                if "titulo" in argumentos:

                    argumentos["titulo"] = (
                        ChatService._limpar_titulo(
                            argumentos["titulo"]
                        )
                    )


                # =================================================
                # EXECUTA TOOL
                # =================================================

                resultado = ToolRegistry.executar(
                    decisao.ferramenta,
                    **argumentos
                )

                # =====================================================
                # ATUALIZA CONTEXTO OPERACIONAL DE TAREFA
                # =====================================================

                if (
                        isinstance(resultado, dict)
                        and resultado.get("id_tarefa") is not None
                        and "tarefa" in str(decisao.ferramenta)
                ):
                    id_tarefa_resultado = resultado.get(
                        "id_tarefa"
                    )

                    titulo_tarefa_resultado = resultado.get(
                        "titulo"
                    )

                    print(
                        "\n===== CONTEXTO DEBUG ====="
                    )

                    print(
                        "Ferramenta:",
                        decisao.ferramenta
                    )

                    print(
                        "Usuário:",
                        id_usuario
                    )

                    print(
                        "Conversa:",
                        id_conversa
                    )

                    print(
                        "ID tarefa:",
                        id_tarefa_resultado
                    )

                    print(
                        "Título:",
                        titulo_tarefa_resultado
                    )

                    print(
                        "==========================\n"
                    )

                    ContextoAgenteService.registrar_tarefa(
                        db=db,
                        id_usuario=id_usuario,
                        id_conversa=id_conversa,
                        id_tarefa=id_tarefa_resultado,
                        ferramenta=decisao.ferramenta
                    )

                    EntidadeContextualService.registrar(
                        db=db,
                        id_usuario=id_usuario,
                        id_conversa=id_conversa,
                        tipo_entidade="TAREFA",
                        id_entidade=id_tarefa_resultado,
                        titulo=titulo_tarefa_resultado
                    )



                # =====================================================
                # REGISTRA LEMBRETE NO CONTEXTO
                # =====================================================

                if (
                        isinstance(resultado, dict)
                        and resultado.get("id_lembrete") is not None
                        and "lembrete" in str(decisao.ferramenta)
                ):
                    EntidadeContextualService.registrar(
                        db=db,
                        id_usuario=id_usuario,
                        id_conversa=id_conversa,
                        tipo_entidade="LEMBRETE",
                        id_entidade=resultado["id_lembrete"],
                        titulo=resultado.get("titulo")
                    )

                # =====================================================
                # ATUALIZA CONTEXTO OPERACIONAL DE LEMBRETE
                # =====================================================

                if (
                    isinstance(resultado, dict)
                    and resultado.get("id_lembrete") is not None
                    and "lembrete" in str(decisao.ferramenta)
                ):
                    ContextoAgenteService.registrar_lembrete(
                        db=db,
                        id_usuario=id_usuario,
                        id_conversa=id_conversa,
                        id_lembrete=resultado["id_lembrete"],
                        ferramenta=decisao.ferramenta
                    )

                # =====================================================
                # ATUALIZA CONTEXTO OPERACIONAL
                # =====================================================




            # =====================================================
            # ERRO FUNCIONAL
            # =====================================================

            except ValueError as erro:

                resposta = str(
                    erro
                )

                ChatInteractionService.salvar_agent(
                    db=db,
                    id_conversa=id_conversa,
                    conteudo_usuario=conteudo,
                    resposta_ara=resposta
                )
                ChatService._extrair_memoria(
                    db=db,
                    id_usuario=id_usuario,
                    conteudo=conteudo
                )


                return {
                    "id_conversa": id_conversa,
                    "mensagem_usuario": conteudo,
                    "resposta_ara": resposta,
                    "modelo": "AGENT",
                    "ferramenta": decisao.ferramenta,
                    "tempo_processamento": 0
                }


            # =====================================================
            # ARGUMENTO OBRIGATÓRIO AUSENTE
            # =====================================================

            except TypeError as erro:

                print(
                    f"Erro de argumentos da ferramenta "
                    f"'{decisao.ferramenta}': {erro}"
                )


                if (
                    "tarefa"
                    in str(decisao.ferramenta)
                ):

                    resposta = (
                        "Preciso saber qual tarefa você "
                        "quer alterar. Me diga o nome dela."
                    )

                elif (
                    "lembrete"
                    in str(decisao.ferramenta)
                ):

                    resposta = (
                        "Preciso saber qual lembrete você "
                        "quer alterar. Me diga qual é."
                    )

                else:

                    resposta = (
                        "Faltou uma informação para eu "
                        "executar essa ação. "
                        "Pode especificar melhor?"
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
                    "ferramenta": decisao.ferramenta,
                    "tempo_processamento": 0
                }


            # =====================================================
            # 6. FORMATA RESPOSTA DA TOOL
            # =====================================================

            resposta = (
                ResponseComposer.formatar_tool(
                    decisao.ferramenta,
                    resultado
                )
            )


            # =====================================================
            # 7. SALVA A INTERAÇÃO
            # =====================================================

            ChatInteractionService.salvar_agent(
                db=db,
                id_conversa=id_conversa,
                conteudo_usuario=conteudo,
                resposta_ara=resposta
            )


            # =====================================================
            # 8. MEMÓRIA
            # =====================================================
            ChatService._extrair_memoria(
                db=db,
                id_usuario=id_usuario,
                conteudo=conteudo
            )



            # =====================================================
            # 9. RETORNO DO AGENT
            # =====================================================

            return {
                "id_conversa": id_conversa,
                "mensagem_usuario": conteudo,
                "resposta_ara": resposta,
                "modelo": "AGENT",
                "ferramenta": decisao.ferramenta,
                "tempo_processamento": 0
            }

        # =========================================================
        # ACTION GUARD
        # =========================================================
        #
        # Se o Agent chegou até aqui, nenhuma ferramenta foi
        # executada.
        #
        # Antes do fallback conversacional, bloqueamos pedidos
        # operacionais conhecidos que não foram confirmados
        # por uma Tool.

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
        ChatService._extrair_memoria(
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
