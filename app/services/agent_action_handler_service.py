from time import perf_counter

from sqlalchemy.orm import Session

from app.agent.agent import AraAgent
from app.agent.intent import TipoAcao
from app.agent.tool_registry import ToolRegistry

from app.ai.response_composer import ResponseComposer

from app.services.confirmation_policy_service import (
    ConfirmationPolicyService
)

from app.services.acao_pendente_service import (
    AcaoPendenteService
)

from app.services.title_cleaner_service import (
    TitleCleanerService
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
from app.services.weather_context_service import WeatherContextService


class AgentActionHandlerService:

    @staticmethod
    def processar(
            db: Session,
            id_usuario: int,
            id_conversa: int,
            conteudo: str,
            localizacao: dict | None = None
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

        decisao = (
            decisao_contextual
            or AraAgent.decidir(
                mensagem=conteudo,
                db=db,
                id_usuario=id_usuario,
                id_conversa=id_conversa
            )
        )



        print(
            f"[PERFORMANCE] Agent: "
            f"{perf_counter() - inicio_agent:.2f}s"
        )

        # =====================================================
        # NÃO É AÇÃO OPERACIONAL
        # =====================================================

        if decisao.acao != TipoAcao.EXECUTAR:
            return None

        argumentos = (
            decisao.argumentos.copy()
            if decisao.argumentos
            else {}
        )


        # =====================================================
        # LOCALIZAÇÃO ATUAL
        # =====================================================

        if (
            decisao.ferramenta
            == "consultar_localizacao_atual"
        ):

            if localizacao:

                latitude = (
                    localizacao.get(
                        "latitude"
                    )
                )

                longitude = (
                    localizacao.get(
                        "longitude"
                    )
                )

                accuracy = (
                    localizacao.get(
                        "accuracy"
                    )
                )


                if (
                    latitude is not None
                    and longitude is not None
                ):

                    argumentos[
                        "latitude"
                    ] = float(
                        latitude
                    )

                    argumentos[
                        "longitude"
                    ] = float(
                        longitude
                    )


                if accuracy is not None:

                    argumentos[
                        "accuracy"
                    ] = float(
                        accuracy
                    )

        # =====================================================
        # LOCALIZAÇÃO ATUAL PARA ROTAS
        # =====================================================

        if decisao.ferramenta == "consultar_rota":

            origem_argumento = str(
                argumentos.get("origem")
                or ""
            ).strip().lower()

            origens_localizacao_atual = {
                "daqui",
                "onde estou",
                "minha localização",
                "minha localizacao",
                "localização atual",
                "localizacao atual"
            }

            if (
                    origem_argumento
                    in origens_localizacao_atual
            ):

                if not localizacao:
                    resposta = (
                        "Preciso da sua localização atual "
                        "para calcular essa rota."
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
                        "ferramenta": "consultar_rota",
                        "tempo_processamento": 0
                    }

                latitude = localizacao.get(
                    "latitude"
                )

                longitude = localizacao.get(
                    "longitude"
                )

                if (
                        latitude is None
                        or longitude is None
                ):
                    raise ValueError(
                        "A localização atual recebida "
                        "não possui coordenadas válidas."
                    )

                argumentos[
                    "origem_latitude"
                ] = float(latitude)

                argumentos[
                    "origem_longitude"
                ] = float(longitude)

        # =====================================================
        # CONFIRMATION POLICY
        # =====================================================

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
                resposta_ara=resposta,
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
        # DADOS INTERNOS
        # =====================================================

        argumentos["db"] = db
        argumentos["id_usuario"] = id_usuario

        try:

            # =================================================
            # LIMPA TÍTULO
            # =================================================

            if "titulo" in argumentos:

                argumentos["titulo"] = (
                    TitleCleanerService.limpar(
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

            # =================================================
            # CONTEXTO DE TAREFA
            # =================================================

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

            # =================================================
            # CONTEXTO DE LEMBRETE
            # =================================================

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
        # ERRO FUNCIONAL
        # =====================================================

        except ValueError as erro:

            resposta = str(erro)

            ChatInteractionService.salvar_agent(
                db=db,
                id_conversa=id_conversa,
                conteudo_usuario=conteudo,
                resposta_ara=resposta
            )

            MemoryExtractionService.processar(
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

            if "tarefa" in str(decisao.ferramenta):

                resposta = (
                    "Preciso saber qual tarefa você "
                    "quer alterar. Me diga o nome dela."
                )

            elif "lembrete" in str(decisao.ferramenta):

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
        # FORMATA RESPOSTA
        # =====================================================

        resposta = ResponseComposer.formatar_tool(
            decisao.ferramenta,
            resultado
        )

        # =====================================================
        # PERSISTÊNCIA
        # =====================================================


        visualizacao = (
            resultado.get("visualizacao")
            if isinstance(resultado, dict)
            else None
        )

        ChatInteractionService.salvar_agent(
            db=db,
            id_conversa=id_conversa,
            conteudo_usuario=conteudo,
            resposta_ara=resposta,
            visualizacao=visualizacao
        )

        # =====================================================
        # MEMÓRIA
        # =====================================================

        MemoryExtractionService.processar(
            db=db,
            id_usuario=id_usuario,
            conteudo=conteudo
        )

        return {
            "id_conversa":
                id_conversa,

            "mensagem_usuario":
                conteudo,

            "resposta_ara":
                resposta,

            "modelo":
                "AGENT",

            "ferramenta":
                decisao.ferramenta,

            "visualizacao":
                resultado.get(
                    "visualizacao"
                )
                if isinstance(
                    resultado,
                    dict
                )
                else None,

            "tempo_processamento":
                0
        }