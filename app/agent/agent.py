from app.services.consulta_instrucional_service import ConsultaInstrucionalService
import json
import re

from app.services.lembrete_service import (
    LembreteService
)

from app.agent.multi_intent_parser import MultiIntentParser

from datetime import timedelta

from sqlalchemy.orm import Session

from app.agent.intent import (
    AgentDecision,
    AgentPlan,
    AgentPlanStep,
    TipoAcao
)

from app.agent.tool_registry import (
    ToolRegistry
)

from app.services.entidade_contextual_service import (
    EntidadeContextualService
)

from app.services.natural_time_service import (
    NaturalTimeService
)

from app.services.tarefa_service import (
    TarefaService
)

from app.services.time_service import (
    TimeService
)

from app.services.contexto_agente_service import ContextoAgenteService


class AraAgent:
    '''
    ===========================================================
    PLANEJAR
    ===========================================================
    '''

    @staticmethod
    def planejar(
            mensagem: str,
            db: Session | None = None,
            id_usuario: int | None = None,
            id_conversa: int | None = None
    ) -> AgentPlan | None:
        """
        Monta um plano para mensagens com múltiplas intenções.

        Suporta:
        - ações independentes;
        - tarefa -> lembrete relativo;
        - mistura de ações dependentes e independentes.
        """

        # =====================================================
        # INSTRUCTIONAL GUARD
        # =====================================================

        consulta_instrucional = (
            ConsultaInstrucionalService.analisar(
                mensagem
            )
        )

        if consulta_instrucional is not None:
            return None

        # =====================================================
        # DIVIDE A MENSAGEM
        # =====================================================

        segmentos = MultiIntentParser.dividir(
            mensagem
        )

        if len(segmentos) < 2:
            return None

        passos: list[AgentPlanStep] = []

        # =====================================================
        # PROCESSA CADA SEGMENTO
        # =====================================================

        for segmento in segmentos:

            # =================================================
            # REFERÊNCIA A UMA AÇÃO ANTERIOR
            # =================================================

            if segmento.referencia_anterior:

                # Por enquanto, a dependência contextual
                # suportada no plano é:
                #
                # criar_tarefa -> criar_lembrete

                indice_tarefa = None
                decisao_tarefa = None

                # Procura a tarefa criada mais recentemente
                # dentro do próprio plano.
                for indice in range(
                        len(passos) - 1,
                        -1,
                        -1
                ):
                    decisao_anterior = (
                        passos[indice].decisao
                    )

                    if (
                            decisao_anterior.ferramenta
                            == "criar_tarefa"
                    ):
                        indice_tarefa = indice
                        decisao_tarefa = (
                            decisao_anterior
                        )
                        break

                if (
                        indice_tarefa is None
                        or decisao_tarefa is None
                ):
                    return None

                data_limite = (
                    decisao_tarefa.argumentos.get(
                        "data_limite"
                    )
                )

                if not data_limite:
                    return None

                # =============================================
                # LEMBRETE RELATIVO
                # =============================================

                match_lembrete = re.search(
                    r"^(?:me\s+)?"
                    r"(?:lembre|lembra)"
                    r"(?:\s+(?:"
                    r"dela|dele|ela|ele|"
                    r"dessa\s+tarefa|"
                    r"desta\s+tarefa|"
                    r"essa\s+tarefa|"
                    r"esta\s+tarefa"
                    r"))?"
                    r"\s+(?P<quantidade>\d+)\s*"
                    r"(?P<unidade>"
                    r"minuto|minutos|hora|horas"
                    r")"
                    r"\s+antes"
                    r"\s*[.!?]*$",
                    segmento.texto,
                    flags=re.IGNORECASE
                )

                if match_lembrete is None:
                    return None

                quantidade = int(
                    match_lembrete.group(
                        "quantidade"
                    )
                )

                unidade = (
                    match_lembrete.group(
                        "unidade"
                    )
                    .lower()
                )

                if unidade.startswith("hora"):
                    offset_minutos = -(
                            quantidade * 60
                    )
                else:
                    offset_minutos = (
                        -quantidade
                    )

                passo_lembrete = AgentPlanStep(
                    decisao=AgentDecision(
                        acao=TipoAcao.EXECUTAR,
                        ferramenta="criar_lembrete",
                        argumentos={
                            "descricao": None,
                            "recorrencia": None
                        }
                    ),
                    depende_de=indice_tarefa,
                    resolver_argumentos={
                        "id_tarefa": {
                            "resultado_de":
                                indice_tarefa,
                            "campo":
                                "id_tarefa"
                        },
                        "titulo": {
                            "resultado_de":
                                indice_tarefa,
                            "campo":
                                "titulo"
                        },
                        "data_hora": {
                            "resultado_de":
                                indice_tarefa,
                            "campo":
                                "data_limite",
                            "offset_minutos":
                                offset_minutos
                        }
                    }
                )

                passos.append(
                    passo_lembrete
                )

                continue

            # =================================================
            # AÇÃO INDEPENDENTE
            # =================================================

            decisao_segmento = (
                AraAgent
                ._detectar_segmento_independente(
                    mensagem=segmento.texto,
                    db=db,
                    id_usuario=id_usuario,
                    id_conversa=id_conversa
                )
            )

            if (
                    decisao_segmento is None
                    or decisao_segmento.acao
                    != TipoAcao.EXECUTAR
                    or not decisao_segmento.ferramenta
            ):
                return None

            passos.append(
                AgentPlanStep(
                    decisao=decisao_segmento
                )
            )

        # =====================================================
        # VALIDA PLANO
        # =====================================================

        if len(passos) < 2:
            return None

        return AgentPlan(
            passos=passos
        )
    # =========================================================
    # DETECTAR SEGMENTO INDEPENDENTE
    # =========================================================

    @staticmethod
    def _detectar_segmento_independente(
            mensagem: str,
            db: Session | None = None,
            id_usuario: int | None = None,
            id_conversa: int | None = None
    ) -> AgentDecision | None:
        """
        Converte um segmento independente em AgentDecision usando
        os detectores determinísticos já existentes.

        Não chama decidir(), porque decidir() também valida o
        ToolRegistry e executa o pipeline público completo do Agent.
        O planner precisa apenas classificar cada segmento.
        """

        # -----------------------------------------------------
        # TAREFAS
        # -----------------------------------------------------

        decisao_tarefa = (
            AraAgent._detectar_acao_tarefa(
                mensagem
            )
        )

        if (
                decisao_tarefa is not None
                and decisao_tarefa.acao == TipoAcao.EXECUTAR
                and decisao_tarefa.ferramenta
        ):
            return decisao_tarefa

        # -----------------------------------------------------
        # EXCLUSÃO EM MASSA DE LEMBRETES
        # -----------------------------------------------------

        decisao_exclusao = (
            AraAgent._detectar_exclusao_todos_lembretes(
                mensagem
            )
        )

        if (
                decisao_exclusao is not None
                and decisao_exclusao.acao == TipoAcao.EXECUTAR
                and decisao_exclusao.ferramenta
        ):
            return decisao_exclusao

        # -----------------------------------------------------
        # AÇÕES DE LEMBRETE
        # -----------------------------------------------------

        decisao_lembrete = (
            AraAgent._detectar_acao_lembrete(
                mensagem
            )
        )

        if (
                decisao_lembrete is not None
                and decisao_lembrete.acao == TipoAcao.EXECUTAR
                and decisao_lembrete.ferramenta
        ):
            return decisao_lembrete

        # -----------------------------------------------------
        # CRIAÇÃO DIRETA DE LEMBRETE
        # -----------------------------------------------------

        decisao_direta = (
            AraAgent._detectar_lembrete(
                mensagem=mensagem,
                db=db,
                id_usuario=id_usuario,
                id_conversa=id_conversa
            )
        )

        if (
                decisao_direta is not None
                and decisao_direta.acao == TipoAcao.EXECUTAR
                and decisao_direta.ferramenta
        ):
            return decisao_direta

        return None

    # =========================================================
    # DECIDIR
    # =========================================================

    @staticmethod
    def decidir(
            mensagem: str,
            db: Session | None = None,
            id_usuario: int | None = None,
            id_conversa: int | None = None
    ) -> AgentDecision:

        # =====================================================
        # FAST PATH — CONVERSAS TRIVIAIS
        # =====================================================

        texto = (
            mensagem
            .lower()
            .strip()
        )

        mensagens_diretas = {
            "oi",
            "olá",
            "ola",
            "e aí",
            "e ai",
            "opa",
            "blz",
            "beleza",
            "valeu",
            "obrigado",
            "obrigada",
            "obg",
            "ok",
            "okay",
            "certo",
            "show",
            "perfeito",
            "entendi",
            "massa",
            "top",
            "bom dia",
            "boa tarde",
            "boa noite",
            "tudo bem",
            "tudo certo"
        }

        if texto in mensagens_diretas:
            print(
                "[AGENT FAST PATH] "
                "Conversa simples detectada."
            )

            return AgentDecision(
                acao=TipoAcao.CONVERSAR
            )

        # =====================================================
        # INSTRUCTIONAL GUARD GLOBAL
        # =====================================================
        #
        # Perguntar COMO executar uma ação não autoriza sua
        # execução. Esta barreira ocorre antes de todos os
        # detectores operacionais.
        # =====================================================

        consulta_instrucional = (
            ConsultaInstrucionalService.analisar(
                mensagem
            )
        )

        if consulta_instrucional is not None:
            return AgentDecision(
                acao=TipoAcao.CONVERSAR
            )

        ferramentas = ToolRegistry.listar()

        contexto_temporal = (
            TimeService.contexto_temporal()
        )

        # =====================================================
        # 1. CONTEXTO DE TAREFA
        #
        # Exemplos:
        # "coloque a primeira como urgente"
        # "joga a segunda para sexta às 19h"
        # "conclua ela"
        # "cancela essa"
        # =====================================================

        decisao_contextual = (
            AraAgent
            ._detectar_acao_contextual_tarefa(
                mensagem=mensagem,
                db=db,
                id_usuario=id_usuario,
                id_conversa=id_conversa
            )
        )

        if (
                decisao_contextual is not None
                and decisao_contextual.acao == TipoAcao.EXECUTAR
                and decisao_contextual.ferramenta
                and ToolRegistry.existe(
            decisao_contextual.ferramenta
        )
        ):
            return decisao_contextual

        # Se o contextual identificou a intenção,
        # mas precisa conversar/solicitar informação.
        if (
                decisao_contextual is not None
                and decisao_contextual.acao == TipoAcao.CONVERSAR
        ):
            return decisao_contextual

        # =====================================================
        # 2. AÇÕES DE TAREFA
        # =====================================================

        decisao_tarefa = (
            AraAgent._detectar_acao_tarefa(
                mensagem
            )
        )

        if (
                decisao_tarefa is not None
                and decisao_tarefa.acao == TipoAcao.EXECUTAR
                and decisao_tarefa.ferramenta
                and ToolRegistry.existe(
            decisao_tarefa.ferramenta
        )
        ):
            return decisao_tarefa

        if (
                decisao_tarefa is not None
                and decisao_tarefa.acao == TipoAcao.CONVERSAR
        ):
            return decisao_tarefa

        decisao_contextual_lembrete = (
            AraAgent
            ._detectar_acao_contextual_lembrete(
                mensagem=mensagem,
                db=db,
                id_usuario=id_usuario,
                id_conversa=id_conversa
            )
        )

        if (
                decisao_contextual_lembrete is not None
                and decisao_contextual_lembrete.ferramenta
                and ToolRegistry.existe(
            decisao_contextual_lembrete.ferramenta
        )
        ):
            return decisao_contextual_lembrete

        # =====================================================
        # 3. EXCLUSÃO EM MASSA DE LEMBRETES
        # =====================================================

        decisao_exclusao_lembretes = (
            AraAgent
            ._detectar_exclusao_todos_lembretes(
                mensagem
            )
        )

        if (
                decisao_exclusao_lembretes is not None
                and decisao_exclusao_lembretes.acao
                == TipoAcao.EXECUTAR
                and decisao_exclusao_lembretes.ferramenta
                and ToolRegistry.existe(
            decisao_exclusao_lembretes.ferramenta
        )
        ):
            return decisao_exclusao_lembretes

        # =====================================================
        # 4. AÇÕES DE LEMBRETE
        # =====================================================

        decisao_lembrete = (
            AraAgent._detectar_acao_lembrete(
                mensagem
            )
        )

        if (
                decisao_lembrete is not None
                and decisao_lembrete.acao == TipoAcao.EXECUTAR
                and decisao_lembrete.ferramenta
                and ToolRegistry.existe(
            decisao_lembrete.ferramenta
        )
        ):
            return decisao_lembrete

        # =====================================================
        # 4. CRIAÇÃO DIRETA DE LEMBRETE
        # =====================================================

        decisao_direta = (
            AraAgent._detectar_lembrete(
                mensagem=mensagem,
                db=db,
                id_usuario=id_usuario,
                id_conversa=id_conversa
            )
        )

        if (
                decisao_direta is not None
                and ToolRegistry.existe(
            "criar_lembrete"
        )
        ):
            return decisao_direta

        # =====================================================
        # 5. FALLBACK DETERMINÍSTICO
        # =====================================================
        #
        # Nenhuma intenção operacional conhecida foi detectada.
        # A mensagem segue diretamente para o fluxo normal de
        # conversação.
        #
        # Isso evita uma chamada adicional ao modelo apenas para
        # classificar mensagens comuns como CONVERSAR.
        # =====================================================

        return AgentDecision(
            acao=TipoAcao.CONVERSAR
        )

    # =========================================================
    # INTERPRETAR RESPOSTA DO MODELO
    # =========================================================

    @staticmethod
    def _interpretar(
            resposta: str
    ) -> AgentDecision:

        resposta = re.sub(
            r"```(?:json)?",
            "",
            resposta,
            flags=re.IGNORECASE
        )

        resposta = resposta.replace(
            "```",
            ""
        ).strip()

        match = re.search(
            r"\{.*\}",
            resposta,
            flags=re.DOTALL
        )

        if match:
            resposta = match.group(0)

        try:

            dados = json.loads(
                resposta
            )

        except json.JSONDecodeError:

            return AgentDecision(
                acao=TipoAcao.CONVERSAR
            )

        acao = str(
            dados.get(
                "acao",
                "CONVERSAR"
            )
        ).upper().strip()

        if acao != "EXECUTAR":
            return AgentDecision(
                acao=TipoAcao.CONVERSAR
            )

        ferramenta = dados.get(
            "ferramenta"
        )

        argumentos = dados.get(
            "argumentos",
            {}
        )

        if not isinstance(
                argumentos,
                dict
        ):
            argumentos = {}

        if (
                not ferramenta
                or not ToolRegistry.existe(
            ferramenta
        )
        ):
            return AgentDecision(
                acao=TipoAcao.CONVERSAR
            )

        argumentos_obrigatorios = {

            "criar_tarefa": [
                "titulo"
            ],

            "iniciar_tarefa": [
                "titulo"
            ],

            "concluir_tarefa": [
                "titulo"
            ],

            "cancelar_tarefa": [
                "titulo"
            ],

            "reabrir_tarefa": [
                "titulo"
            ],

            "editar_tarefa": [
                "titulo"
            ],

            "criar_lembrete": [
                "titulo",
                "data_hora"
            ],

            "cancelar_lembrete": [
                "titulo"
            ],

            "concluir_lembrete": [
                "titulo"
            ]
        }

        obrigatorios = (
            argumentos_obrigatorios.get(
                ferramenta,
                []
            )
        )

        for argumento in obrigatorios:

            valor = argumentos.get(
                argumento
            )

            if valor is None:
                return AgentDecision(
                    acao=TipoAcao.CONVERSAR
                )

            if (
                    isinstance(valor, str)
                    and not valor.strip()
            ):
                return AgentDecision(
                    acao=TipoAcao.CONVERSAR
                )

        return AgentDecision(
            acao=TipoAcao.EXECUTAR,
            ferramenta=ferramenta,
            argumentos=argumentos
        )

    # =========================================================
    # LIMPAR TÍTULO
    # =========================================================

    @staticmethod
    def _limpar_titulo(
            titulo: str
    ) -> str:

        if not titulo:
            return ""

        titulo = titulo.strip()

        # =====================================================
        # EXPRESSÕES DE EDUCAÇÃO
        # =====================================================

        titulo = re.sub(
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
            titulo,
            flags=(
                    re.IGNORECASE
                    | re.VERBOSE
            )
        )

        # =====================================================
        # EXPRESSÕES DE PRIORIDADE
        # =====================================================

        titulo = re.sub(
            r"\bprioridade\s+"
            r"(máxima|maxima|alta|baixa|muito baixa|[1-5])\b",
            "",
            titulo,
            flags=re.IGNORECASE
        )

        titulo = re.sub(
            r"\b("
            r"muito urgente|"
            r"urgentemente|"
            r"urgente|"
            r"alta prioridade|"
            r"baixa prioridade|"
            r"muito baixa prioridade"
            r")\b",
            "",
            titulo,
            flags=re.IGNORECASE
        )

        # =====================================================
        # NORMALIZA ESPAÇOS
        # =====================================================

        titulo = re.sub(
            r"\s+",
            " ",
            titulo
        )

        titulo = titulo.strip(
            " ,.!?;:-"
        )

        # =====================================================
        # PREFIXOS
        # =====================================================

        titulo = re.sub(
            r"^(para|de|do|da)\s+",
            "",
            titulo,
            flags=re.IGNORECASE
        )

        return titulo.strip(
            " ,.!?;:-"
        )

    # =========================================================
    # DETECTAR PRIORIDADE
    # =========================================================

    @staticmethod
    def _detectar_prioridade(
            mensagem: str
    ) -> int:

        texto = mensagem.lower()

        # =====================================================
        # PRIORIDADE 5
        # =====================================================

        palavras_urgentes = [
            "muito urgente",
            "urgentemente",
            "urgente",
            "prioridade máxima",
            "prioridade maxima",
            "prioridade 5"
        ]

        for termo in palavras_urgentes:

            if termo in texto:
                return 5

        # =====================================================
        # PRIORIDADE 4
        # =====================================================

        palavras_altas = [
            "prioridade alta",
            "alta prioridade",
            "prioridade 4",
            "importante"
        ]

        for termo in palavras_altas:

            if termo in texto:
                return 4

        # =====================================================
        # PRIORIDADE 1
        # =====================================================

        palavras_muito_baixas = [
            "prioridade muito baixa",
            "muito baixa prioridade",
            "prioridade 1"
        ]

        for termo in palavras_muito_baixas:

            if termo in texto:
                return 1

        # =====================================================
        # PRIORIDADE 2
        # =====================================================

        palavras_baixas = [
            "prioridade baixa",
            "baixa prioridade",
            "prioridade 2",
            "não é importante",
            "nao é importante",
            "nao e importante"
        ]

        for termo in palavras_baixas:

            if termo in texto:
                return 2

        # =====================================================
        # PRIORIDADE 3
        # =====================================================

        return 3

    # =========================================================
    # EXCLUIR TODOS OS LEMBRETES
    # =========================================================

    @staticmethod
    def _detectar_exclusao_todos_lembretes(
            mensagem: str
    ) -> AgentDecision | None:

        texto = (
            mensagem
            .lower()
            .strip()
        )

        # -----------------------------------------------------
        # QUERY / INSTRUCTION GUARD
        #
        # Perguntar COMO fazer uma operação não significa
        # solicitar que ela seja executada.
        #
        # Exemplos:
        # "como excluir todos os lembretes?"
        # "como posso apagar todos os lembretes?"
        # "me ensine a excluir todos os lembretes"
        # -----------------------------------------------------

        padroes_instrucionais = (
            r"^como\b",
            r"^me\s+ensine\b",
            r"^me\s+explique\b",
            r"^explique\b",
            r"^me\s+mostre\s+como\b",
            r"^me\s+diga\s+como\b",
            r"^quero\s+saber\s+como\b",
            r"^gostaria\s+de\s+saber\s+como\b",
            r"^posso\b",
            r"^eu\s+consigo\b",
            r"^qual\s+(?:e|é|seria)\s+"
            r"(?:a\s+)?(?:forma|maneira)\b",
            r"^qual\s+(?:e|é|seria)\s+"
            r"(?:o\s+)?jeito\b",
        )

        if any(
                re.search(
                    padrao,
                    texto
                )
                for padrao in padroes_instrucionais
        ):
            return None

        # -----------------------------------------------------
        # A intenção precisa conter:
        #
        # 1. verbo explícito de exclusão;
        # 2. quantificador de totalidade;
        # 3. domínio lembrete.
        #
        # Isso evita interpretar exclusões individuais como
        # exclusões em massa.
        # -----------------------------------------------------

        verbo_exclusao = bool(
            re.search(
                r"\b(?:"
                r"exclua|excluir|exclui|"
                r"apague|apagar|"
                r"delete|deletar|"
                r"remova|remover"
                r")\b",
                texto
            )
        )

        totalidade = bool(
            re.search(
                r"\b(?:"
                r"todos|todas"
                r")\b",
                texto
            )
        )

        dominio_lembrete = bool(
            re.search(
                r"\blembretes?\b",
                texto
            )
        )

        if not (
                verbo_exclusao
                and totalidade
                and dominio_lembrete
        ):
            return None

        return AgentDecision(
            acao=TipoAcao.EXECUTAR,
            ferramenta="excluir_todos_lembretes",
            argumentos={}
        )

    # =========================================================
    # DETECTAR LEMBRETE
    # =========================================================

    @staticmethod
    def _detectar_lembrete(
            mensagem: str,
            db: Session | None = None,
            id_usuario: int | None = None,
            id_conversa: int | None = None
    ) -> AgentDecision | None:

        texto = mensagem.lower().strip()

        gatilhos = [
            "me lembra",
            "me lembre",
            "lembra de",
            "lembre de",
            "cria um lembrete",
            "crie um lembrete"
        ]

        if not any(
                gatilho in texto
                for gatilho in gatilhos
        ):
            return None

        # =====================================================
        # REMINDER BRIDGE — REFERÊNCIA À ÚLTIMA TAREFA
        #
        # Exemplos:
        # "crie um lembrete para ela 30 minutos antes"
        # "me lembre dela 1 hora antes"
        #
        # A referência contextual aponta para a última tarefa
        # válida da conversa. O horário do lembrete é calculado
        # a partir de data_limite da tarefa.
        # =====================================================

        referencia_tarefa = bool(
            re.search(
                r"\b(?:"
                r"ela|ele|"
                r"essa\s+tarefa|"
                r"esta\s+tarefa|"
                r"esse\s+tarefa|"
                r"este\s+tarefa"
                r")\b",
                texto
            )
        )

        deslocamento_antes = re.search(
            r"\b(\d+)\s*"
            r"(minuto|minutos|hora|horas)\s+antes\b",
            texto
        )

        if (
                referencia_tarefa
                and deslocamento_antes is not None
        ):

            if (
                    db is None
                    or id_usuario is None
                    or id_conversa is None
            ):
                return AgentDecision(
                    acao=TipoAcao.CONVERSAR
                )

            id_tarefa = (
                ContextoAgenteService
                .obter_ultima_tarefa_id(
                    db=db,
                    id_usuario=id_usuario,
                    id_conversa=id_conversa
                )
            )

            if id_tarefa is None:
                return AgentDecision(
                    acao=TipoAcao.CONVERSAR
                )

            try:

                tarefa = TarefaService.buscar_por_id(
                    db,
                    id_tarefa
                )

            except ValueError:

                return AgentDecision(
                    acao=TipoAcao.CONVERSAR
                )

            if tarefa.id_usuario != id_usuario:
                return AgentDecision(
                    acao=TipoAcao.CONVERSAR
                )

            data_limite = getattr(
                tarefa,
                "data_limite",
                None
            )

            if data_limite is None:
                return AgentDecision(
                    acao=TipoAcao.CONVERSAR
                )

            quantidade = int(
                deslocamento_antes.group(1)
            )

            unidade = (
                deslocamento_antes
                .group(2)
            )

            if unidade.startswith("hora"):
                deslocamento = timedelta(
                    hours=quantidade
                )
            else:
                deslocamento = timedelta(
                    minutes=quantidade
                )

            data_lembrete = (
                    data_limite
                    - deslocamento
            )

            # =====================================================
            # NORMALIZAÇÃO DE TIMEZONE
            #
            # MariaDB/MySQL DATETIME não preserva timezone.
            # TimeService.agora(), por outro lado, pode retornar
            # um datetime timezone-aware.
            #
            # Antes de comparar, os dois valores precisam usar
            # a mesma referência temporal.
            # =====================================================

            agora_referencia = TimeService.agora()

            if (
                    data_lembrete.tzinfo is None
                    and agora_referencia.tzinfo is not None
            ):
                data_lembrete = data_lembrete.replace(
                    tzinfo=agora_referencia.tzinfo
                )

            elif (
                    data_lembrete.tzinfo is not None
                    and agora_referencia.tzinfo is None
            ):
                agora_referencia = agora_referencia.replace(
                    tzinfo=data_lembrete.tzinfo
                )

            # Não cria lembrete contextual já vencido.
            if data_lembrete <= agora_referencia:
                return AgentDecision(
                    acao=TipoAcao.CONVERSAR
                )

            return AgentDecision(
                acao=TipoAcao.EXECUTAR,
                ferramenta="criar_lembrete",
                argumentos={
                    "titulo": tarefa.titulo,
                    "data_hora":
                        data_lembrete.isoformat(),
                    "descricao": None,
                    "recorrencia": None,
                    "id_tarefa": tarefa.id_tarefa
                }
            )

        agora = TimeService.agora()

        if (
                "depois de amanhã" in texto
                or "depois de amanha" in texto
        ):

            data_alvo = (
                    agora
                    + timedelta(days=2)
            )

        elif (
                "amanhã" in texto
                or "amanha" in texto
        ):

            data_alvo = (
                    agora
                    + timedelta(days=1)
            )

        elif "hoje" in texto:

            data_alvo = agora

        else:

            # Tenta interpretação mais avançada.
            data_alvo = (
                NaturalTimeService.interpretar(
                    mensagem
                )
            )

            if data_alvo is None:
                return None

        # =====================================================
        # HORÁRIO
        # =====================================================

        horario = re.search(
            r"\b([01]?\d|2[0-3])"
            r"(?:[:h](\d{2}))?"
            r"(?:\s*h)?\b",
            texto
        )

        if horario is not None:
            hora = int(
                horario.group(1)
            )

            minuto = int(
                horario.group(2)
                or 0
            )

            data_alvo = data_alvo.replace(
                hour=hora,
                minute=minuto,
                second=0,
                microsecond=0
            )

        # =====================================================
        # TÍTULO
        # =====================================================

        titulo = mensagem

        titulo = re.sub(
            r"(?i)\b(?:a\.?r\.?a\.?|ara)\b[,\s]*",
            "",
            titulo
        )

        titulo = re.sub(
            r"(?i)\b("
            r"me lembra|"
            r"me lembre|"
            r"lembra de|"
            r"lembre de|"
            r"cria um lembrete|"
            r"crie um lembrete"
            r")\s+(de\s+)?",
            "",
            titulo
        )

        titulo = (
            NaturalTimeService
            .remover_tempo_do_texto(
                titulo
            )
        )

        titulo = (
            AraAgent._limpar_titulo(
                titulo
            )
        )

        if not titulo:
            titulo = "Lembrete"

        return AgentDecision(
            acao=TipoAcao.EXECUTAR,
            ferramenta="criar_lembrete",
            argumentos={
                "titulo": titulo,
                "data_hora": data_alvo.isoformat(),
                "descricao": None,
                "recorrencia": None
            }
        )

    # =========================================================
    # AÇÕES DE LEMBRETES
    # =========================================================

    @staticmethod
    def _detectar_acao_lembrete(
            mensagem: str
    ) -> AgentDecision | None:

        texto = mensagem.lower().strip()

        # =====================================================
        # LISTAR
        # =====================================================

        gatilhos_listar = [
            "meus lembretes",
            "meus lembretes?",
            "quais lembretes",
            "listar lembretes",
            "lista meus lembretes",
            "tenho algum lembrete",
            "tenho lembretes"
        ]

        if any(
                gatilho in texto
                for gatilho in gatilhos_listar
        ):
            return AgentDecision(
                acao=TipoAcao.EXECUTAR,
                ferramenta="listar_lembretes",
                argumentos={}
            )

        # =====================================================
        # CANCELAR
        # =====================================================

        gatilhos_cancelar = [
            "cancela o lembrete",
            "cancele o lembrete",
            "cancelar lembrete",
            "apaga o lembrete",
            "apague o lembrete"
        ]

        for gatilho in gatilhos_cancelar:

            if gatilho in texto:

                titulo = texto.split(
                    gatilho,
                    1
                )[1].strip()

                titulo = re.sub(
                    r"^(de|do|da)\s+",
                    "",
                    titulo
                )

                titulo = (
                    AraAgent._limpar_titulo(
                        titulo
                    )
                )

                if titulo:
                    return AgentDecision(
                        acao=TipoAcao.EXECUTAR,
                        ferramenta="cancelar_lembrete",
                        argumentos={
                            "titulo": titulo
                        }
                    )

        # =====================================================
        # CONCLUIR
        # =====================================================

        gatilhos_concluir = [
            "conclui o lembrete",
            "concluir lembrete",
            "marque como concluído",
            "marca como concluído",
            "marque como concluido",
            "marca como concluido"
        ]

        for gatilho in gatilhos_concluir:

            if gatilho in texto:

                titulo = texto.split(
                    gatilho,
                    1
                )[1].strip()

                titulo = re.sub(
                    r"^(de|do|da)\s+",
                    "",
                    titulo
                )

                titulo = (
                    AraAgent._limpar_titulo(
                        titulo
                    )
                )

                if titulo:
                    return AgentDecision(
                        acao=TipoAcao.EXECUTAR,
                        ferramenta="concluir_lembrete",
                        argumentos={
                            "titulo": titulo
                        }
                    )

        return None

    # =========================================================
    # RESOLVER TAREFA CONTEXTUAL
    # =========================================================

    @staticmethod
    def _resolver_tarefa_contextual(
            mensagem: str,
            db: Session | None,
            id_usuario: int | None,
            id_conversa: int | None
    ):

        if (
                db is None
                or id_usuario is None
                or id_conversa is None
        ):
            return None

        entidade = (
            EntidadeContextualService
            .resolver_referencia(
                db=db,
                id_usuario=id_usuario,
                id_conversa=id_conversa,
                texto=mensagem
            )
        )

        if entidade is None:

            # =================================================
            # CONTINUAÇÃO IMPLÍCITA DE PRIORIDADE
            # =================================================
            #
            # Exemplos:
            #
            # "prioridade alta também"
            # "coloque prioridade alta também"
            #
            # Não usamos a última tarefa como fallback global.
            # Isso só ocorre quando há evidência clara de uma
            # continuação de prioridade.

            texto_contextual = (
                EntidadeContextualService
                ._normalizar_texto(
                    mensagem
                )
            )

            possui_continuacao = bool(
                re.search(
                    r"\btambem\b",
                    texto_contextual
                )
            )

            possui_prioridade = bool(
                re.search(
                    r"\b(?:"
                    r"prioridade"
                    r"|urgente"
                    r"|importante"
                    r"|muito\s+baixa"
                    r"|baixa"
                    r"|normal"
                    r"|alta"
                    r")\b",
                    texto_contextual
                )
            )

            eh_continuacao_prioridade = (
                    possui_continuacao
                    and possui_prioridade
            )

            if not eh_continuacao_prioridade:
                return None

            id_tarefa_contextual = (
                ContextoAgenteService
                .obter_ultima_tarefa_id(
                    db=db,
                    id_usuario=id_usuario,
                    id_conversa=id_conversa
                )
            )

            if id_tarefa_contextual is None:
                return None

            try:

                tarefa = (
                    TarefaService.buscar_por_id(
                        db,
                        id_tarefa_contextual
                    )
                )

            except ValueError:
                return None

            if tarefa.id_usuario != id_usuario:
                return None

            return tarefa

        try:

            tarefa = (
                TarefaService.buscar_por_id(
                    db,
                    entidade.id_entidade
                )
            )

        except ValueError:

            return None

        # =====================================================
        # SEGURANÇA
        # =====================================================

        if tarefa.id_usuario != id_usuario:
            return None

        return tarefa

    # =========================================================
    # DETECTAR AÇÃO CONTEXTUAL DE TAREFA
    # =========================================================

    @staticmethod
    def _detectar_acao_contextual_tarefa(
            mensagem: str,
            db: Session | None,
            id_usuario: int | None,
            id_conversa: int | None
    ) -> AgentDecision | None:

        if (
                db is None
                or id_usuario is None
                or id_conversa is None
        ):
            return None

        texto = mensagem.lower().strip()

        # =====================================================
        # CONSULTA CONTEXTUAL DE LISTAGEM
        # =====================================================
        #
        # Continuação natural de uma conversa sobre lembretes:
        #
        # "todos"
        # "todos eles"
        # "mostra todos"
        # "lista todos"
        # "e os outros"
        #
        # Nunca deve cair no LLM, porque a lista precisa vir
        # obrigatoriamente do banco.
        # =====================================================

        consultas_listagem = {
            "todos",
            "todos eles",
            "todos os lembretes",
            "lista todos",
            "liste todos",
            "mostra todos",
            "mostre todos",
            "e os outros",
            "e os demais",
        }

        if texto in consultas_listagem:

            id_ultimo_lembrete = (
                ContextoAgenteService
                .obter_ultimo_lembrete_id(
                    db=db,
                    id_usuario=id_usuario,
                    id_conversa=id_conversa
                )
            )

            if id_ultimo_lembrete is not None:
                return AgentDecision(
                    acao=TipoAcao.EXECUTAR,
                    ferramenta="listar_lembretes",
                    argumentos={}
                )

        # =====================================================
        # GUARDA DE MUTAÇÃO CONTEXTUAL
        # =====================================================
        #
        # O contexto pode resolver QUAL tarefa está em foco,
        # mas nunca pode inventar QUAL ação o usuário deseja.
        #
        # Frases como:
        # "está faltando..."
        # "não apareceu..."
        # "cadê..."
        # "e aquela?"
        #
        # são observações/consultas, não comandos de alteração.
        # =====================================================

        gatilhos_operacionais = [
            # prazo / edição
            "muda",
            "mude",
            "altera",
            "altere",
            "troca",
            "troque",
            "joga",
            "jogue",
            "coloca",
            "coloque",
            "passa",
            "passe",
            "remove",
            "remova",
            "tira",
            "tire",

            # status
            "inicia",
            "inicie",
            "começa",
            "comece",
            "conclui",
            "conclua",
            "finaliza",
            "finalize",
            "cancela",
            "cancele",
            "reabre",
            "reabra",

            # exclusão
            "exclui",
            "exclua",
            "apaga",
            "apague",

            # prioridade
            "prioridade",
            "urgente",
            "muito baixa",
            "baixa",
            "alta",
        ]

        tem_intencao_operacional = any(
            re.search(
                rf"(?<!\w){re.escape(gatilho)}(?!\w)",
                texto,
                flags=re.IGNORECASE
            )
            is not None
            for gatilho in gatilhos_operacionais
        )

        if not tem_intencao_operacional:
            return None

        # Se a mensagem fala explicitamente de lembrete,
        # ela não pode ser capturada pelo contexto de tarefa.
        if "lembrete" in texto:
            return None

        # =====================================================
        # RESOLVE REFERÊNCIA
        # =====================================================

        tarefa = (
            AraAgent._resolver_tarefa_contextual(
                mensagem=mensagem,
                db=db,
                id_usuario=id_usuario,
                id_conversa=id_conversa
            )
        )

        # =====================================================
        # CONSULTA CONTEXTUAL DE LEMBRETE
        # =====================================================

        contexto = ContextoAgenteService.obter(
            db=db,
            id_usuario=id_usuario,
            id_conversa=id_conversa
        )

        ultima_ferramenta = getattr(
            contexto,
            "ultima_ferramenta",
            None
        )

        contexto_lembrete = (
                "lembrete" in texto
                or ultima_ferramenta in {
                    "criar_lembrete",
                    "listar_lembretes",
                    "consultar_lembrete",
                    "editar_lembrete",
                    "cancelar_lembrete",
                    "concluir_lembrete"
                }
        )

        if contexto_lembrete:

            padroes_consulta = [
                r"^(?:está|esta)\s+faltando\s+(?:o|a)?\s*(.+)$",
                r"^faltando\s+(?:o|a)?\s*(.+)$",
                r"^(?:não|nao)\s+apareceu\s+(?:o|a)?\s*(.+)$",
                r"^(?:cadê|cade)\s+(?:o|a)?\s*(.+)$",
            ]

            for padrao in padroes_consulta:

                match = re.match(
                    padrao,
                    texto,
                    flags=re.IGNORECASE
                )

                if match:

                    titulo = (
                        match.group(1)
                        .strip(" .?!")
                    )

                    if titulo:
                        return AgentDecision(
                            acao=TipoAcao.EXECUTAR,
                            ferramenta="consultar_lembrete",
                            argumentos={
                                "titulo": titulo
                            }
                        )

        # =====================================================
        # DEBUG TEMPORÁRIO
        # =====================================================

        print(
            "\n===== CONTEXTO AGENT DEBUG ====="
        )

        print(
            "Mensagem:",
            mensagem
        )

        print(
            "Tarefa resolvida:",
            tarefa.titulo
            if tarefa
            else None
        )

        print(
            "ID:",
            tarefa.id_tarefa
            if tarefa
            else None
        )

        print(
            "================================\n"
        )

        if tarefa is None:
            return None

        titulo = tarefa.titulo

        # =====================================================
        # REMOVER PRAZO
        # =====================================================

        gatilhos_remover_prazo = [
            "sem prazo",
            "remove o prazo",
            "remova o prazo",
            "tira o prazo",
            "tire o prazo"
        ]

        if any(
                gatilho in texto
                for gatilho in gatilhos_remover_prazo
        ):
            return AgentDecision(
                acao=TipoAcao.EXECUTAR,
                ferramenta="editar_tarefa",
                argumentos={
                    "titulo": titulo,
                    "remover_data_limite": True
                }
            )

        # =====================================================
        # ALTERAR PRAZO
        # =====================================================

        gatilhos_prazo = [
            "joga",
            "jogue",
            "muda o prazo",
            "mude o prazo",
            "altera o prazo",
            "altere o prazo",
            "coloca para",
            "coloque para",
            "passa para",
            "passe para",

            # continuações naturais
            "muda ela para",
            "mude ela para",
            "muda ela pra",
            "mude ela pra",

            "muda essa para",
            "mude essa para",
            "muda essa pra",
            "mude essa pra",

            "muda esta para",
            "mude esta para",
            "muda esta pra",
            "mude esta pra",

            "coloca ela para",
            "coloque ela para",
            "coloca ela pra",
            "coloque ela pra",

            "coloca essa para",
            "coloque essa para",
            "coloca essa pra",
            "coloque essa pra",

            "coloca esta para",
            "coloque esta para",
            "coloca esta pra",
            "coloque esta pra"
        ]

        if any(
                gatilho in texto
                for gatilho in gatilhos_prazo
        ):

            data_limite = (
                NaturalTimeService.interpretar(
                    mensagem
                )
            )

            print(
                "===== PRAZO CONTEXTUAL DEBUG ====="
            )

            print(
                "Mensagem:",
                mensagem
            )

            print(
                "Data detectada:",
                data_limite
            )

            print(
                "=================================="
            )

            # =================================================
            # HORÁRIO ISOLADO
            # =================================================
            #
            # NaturalTimeService pode não interpretar:
            #
            # "mude ela para 21h"
            # "coloque ela para 22h30"
            #
            # Se a tarefa já possui data_limite, preservamos
            # sua data e alteramos apenas hora/minuto.

            if (
                    data_limite is None
                    and tarefa.data_limite is not None
            ):

                horario_match = re.search(
                    r"(?<!\d)"
                    r"([01]?\d|2[0-3])"
                    r"(?:"
                    r"\s*[hH]\s*([0-5]?\d)?"
                    r"|"
                    r":([0-5]\d)"
                    r")"
                    r"(?!\d)",
                    mensagem
                )

                if horario_match:
                    hora = int(
                        horario_match.group(1)
                    )

                    minuto_texto = (
                            horario_match.group(2)
                            or horario_match.group(3)
                    )

                    minuto = (
                        int(minuto_texto)
                        if minuto_texto
                        else 0
                    )

                    data_atual = (
                        tarefa.data_limite
                    )

                    data_limite = (
                        data_atual.replace(
                            hour=hora,
                            minute=minuto,
                            second=0,
                            microsecond=0
                        )
                    )

            if data_limite is not None:
                return AgentDecision(
                    acao=TipoAcao.EXECUTAR,
                    ferramenta="editar_tarefa",
                    argumentos={
                        "titulo": titulo,
                        "data_limite":
                            data_limite.isoformat()
                    }
                )

        # =====================================================
        # CONSULTA CONTEXTUAL DA TAREFA — READ-ONLY
        # =====================================================

        texto_consulta = (
            EntidadeContextualService
            ._normalizar_texto(
                mensagem
            )
        )

        # -----------------------------------------------------
        # PRIORIDADE
        # -----------------------------------------------------

        eh_consulta_prioridade = bool(
            re.search(
                r"^(?:"
                r"qual\s+(?:e\s+|seria\s+)?a\s+prioridade"
                r"|qual\s+prioridade"
                r"|que\s+prioridade"
                r")\b",
                texto_consulta
            )
        )

        if eh_consulta_prioridade:
            return AgentDecision(
                acao=TipoAcao.EXECUTAR,
                ferramenta="consultar_tarefa",
                argumentos={
                    "titulo": titulo,
                    "campo": "prioridade"
                }
            )

        # -----------------------------------------------------
        # STATUS
        # -----------------------------------------------------

        eh_consulta_status = bool(
            re.search(
                r"^(?:"
                r"qual\s+(?:e\s+|seria\s+)?o\s+status"
                r"|qual\s+status"
                r"|que\s+status"
                r")\b",
                texto_consulta
            )
        )

        if eh_consulta_status:
            return AgentDecision(
                acao=TipoAcao.EXECUTAR,
                ferramenta="consultar_tarefa",
                argumentos={
                    "titulo": titulo,
                    "campo": "status"
                }
            )

        # -----------------------------------------------------
        # PRAZO
        # -----------------------------------------------------

        eh_consulta_prazo = bool(
            re.search(
                r"^(?:"
                r"qual\s+(?:e\s+|seria\s+)?o\s+prazo"
                r"|qual\s+prazo"
                r"|quando\s+.*(?:vence|termina)"
                r"|que\s+horas?\s+.*(?:vence|termina)"
                r")\b",
                texto_consulta
            )
        )

        if eh_consulta_prazo:
            return AgentDecision(
                acao=TipoAcao.EXECUTAR,
                ferramenta="consultar_tarefa",
                argumentos={
                    "titulo": titulo,
                    "campo": "data_limite"
                }
            )

        # =====================================================
        # ALTERAR PRIORIDADE
        # =====================================================

        termos_prioridade = [
            "urgente",
            "prioridade",
            "importante",
            "muito baixa",
            "baixa",
            "normal",
            "alta"
        ]

        if any(
                termo in texto
                for termo in termos_prioridade
        ):
            prioridade = (
                AraAgent._detectar_prioridade(
                    mensagem
                )
            )

            return AgentDecision(
                acao=TipoAcao.EXECUTAR,
                ferramenta="editar_tarefa",
                argumentos={
                    "titulo": titulo,
                    "prioridade": prioridade
                }
            )

        # =====================================================
        # REABRIR
        # =====================================================

        gatilhos_reabrir = [
            "reabre",
            "reabra",
            "reabrir",
            "refaz",
            "refaça",
            "refazer",
            "fazer de novo"
        ]

        if any(
                gatilho in texto
                for gatilho in gatilhos_reabrir
        ):
            return AgentDecision(
                acao=TipoAcao.EXECUTAR,
                ferramenta="reabrir_tarefa",
                argumentos={
                    "titulo": titulo
                }
            )

        # =====================================================
        # CONCLUIR
        # =====================================================

        gatilhos_concluir = [
            "conclui",
            "conclua",
            "finaliza",
            "finalize",
            "termina",
            "terminei",
            "marque como concluída",
            "marque como concluida",
            "marca como concluída",
            "marca como concluida"
        ]

        if any(
                gatilho in texto
                for gatilho in gatilhos_concluir
        ):
            return AgentDecision(
                acao=TipoAcao.EXECUTAR,
                ferramenta="concluir_tarefa",
                argumentos={
                    "titulo": titulo
                }
            )

        # =====================================================
        # INICIAR
        # =====================================================

        gatilhos_iniciar = [
            "inicia",
            "inicie",
            "começa",
            "comece",
            "começar"
        ]

        if any(
                gatilho in texto
                for gatilho in gatilhos_iniciar
        ):
            return AgentDecision(
                acao=TipoAcao.EXECUTAR,
                ferramenta="iniciar_tarefa",
                argumentos={
                    "titulo": titulo
                }
            )

        # =====================================================
        # CANCELAR
        # =====================================================

        gatilhos_cancelar = [
            "cancela",
            "cancele",
            "cancelar",
            "exclui",
            "excluir"
        ]

        if any(
                gatilho in texto
                for gatilho in gatilhos_cancelar
        ):
            return AgentDecision(
                acao=TipoAcao.EXECUTAR,
                ferramenta="cancelar_tarefa",
                argumentos={
                    "titulo": titulo
                }
            )

        return None

    # =========================================================
    # DETECTAR AÇÕES DE TAREFA
    # =========================================================

    @staticmethod
    def _detectar_acao_tarefa(
            mensagem: str
    ) -> AgentDecision | None:

        texto = mensagem.lower().strip()

        # =====================================================
        # TAREFAS DE HOJE
        # =====================================================

        if (
                "tarefas de hoje" in texto
                or "tarefas para hoje" in texto
                or "o que tenho para hoje" in texto
                or "o que eu tenho para hoje" in texto
        ):
            agora = TimeService.agora()

            inicio = agora.replace(
                hour=0,
                minute=0,
                second=0,
                microsecond=0
            )

            fim = agora.replace(
                hour=23,
                minute=59,
                second=59,
                microsecond=999999
            )

            return AgentDecision(
                acao=TipoAcao.EXECUTAR,
                ferramenta="listar_tarefas_periodo",
                argumentos={
                    "inicio": inicio.isoformat(),
                    "fim": fim.isoformat()
                }
            )

        # =====================================================
        # TAREFAS DE AMANHÃ
        # =====================================================

        if (
                "tarefas de amanhã" in texto
                or "tarefas de amanha" in texto
                or "tarefas para amanhã" in texto
                or "tarefas para amanha" in texto
        ):
            agora = TimeService.agora()

            amanha = (
                    agora
                    + timedelta(days=1)
            )

            inicio = amanha.replace(
                hour=0,
                minute=0,
                second=0,
                microsecond=0
            )

            fim = amanha.replace(
                hour=23,
                minute=59,
                second=59,
                microsecond=999999
            )

            return AgentDecision(
                acao=TipoAcao.EXECUTAR,
                ferramenta="listar_tarefas_periodo",
                argumentos={
                    "inicio": inicio.isoformat(),
                    "fim": fim.isoformat()
                }
            )

        # =====================================================
        # LISTAR
        # =====================================================

        gatilhos_listar = [
            "quais tarefas",
            "minhas tarefas",
            "listar tarefas",
            "lista minhas tarefas",
            "tenho tarefas",
            "tarefas pendentes"
        ]

        if any(
                gatilho in texto
                for gatilho in gatilhos_listar
        ):
            return AgentDecision(
                acao=TipoAcao.EXECUTAR,
                ferramenta="listar_tarefas",
                argumentos={}
            )

        # =====================================================
        # RENOMEAR
        # =====================================================

        padroes_renomear = [
            r"renomeie a tarefa (.+?) para (.+)",
            r"renomeia a tarefa (.+?) para (.+)",
            r"mude o nome da tarefa (.+?) para (.+)",
            r"altere o nome da tarefa (.+?) para (.+)"
        ]

        for padrao in padroes_renomear:

            match = re.search(
                padrao,
                texto,
                flags=re.IGNORECASE
            )

            if match:
                titulo = (
                    AraAgent._limpar_titulo(
                        match.group(1)
                    )
                )

                novo_titulo = (
                    AraAgent._limpar_titulo(
                        match.group(2)
                    )
                )

                return AgentDecision(
                    acao=TipoAcao.EXECUTAR,
                    ferramenta="editar_tarefa",
                    argumentos={
                        "titulo": titulo,
                        "novo_titulo": novo_titulo
                    }
                )

        # =====================================================
        # ALTERAR PRIORIDADE NUMÉRICA
        # =====================================================

        padroes_prioridade = [
            r"altere a prioridade da tarefa (.+?) para ([1-5])",
            r"mude a prioridade da tarefa (.+?) para ([1-5])",
            r"coloque a prioridade da tarefa (.+?) em ([1-5])",
            r"defina a prioridade da tarefa (.+?) como ([1-5])"
        ]

        for padrao in padroes_prioridade:

            match = re.search(
                padrao,
                texto,
                flags=re.IGNORECASE
            )

            if match:
                titulo = (
                    AraAgent._limpar_titulo(
                        match.group(1)
                    )
                )

                prioridade = int(
                    match.group(2)
                )

                return AgentDecision(
                    acao=TipoAcao.EXECUTAR,
                    ferramenta="editar_tarefa",
                    argumentos={
                        "titulo": titulo,
                        "prioridade": prioridade
                    }
                )

        # =====================================================
        # ALTERAR DESCRIÇÃO
        # =====================================================

        padroes_descricao = [
            r"altere a descrição da tarefa (.+?) para (.+)",
            r"mude a descrição da tarefa (.+?) para (.+)",
            r"coloque na descrição da tarefa (.+?):? (.+)"
        ]

        for padrao in padroes_descricao:

            match = re.search(
                padrao,
                texto,
                flags=re.IGNORECASE
            )

            if match:
                titulo = (
                    AraAgent._limpar_titulo(
                        match.group(1)
                    )
                )

                descricao = (
                    match.group(2)
                    .strip()
                )

                return AgentDecision(
                    acao=TipoAcao.EXECUTAR,
                    ferramenta="editar_tarefa",
                    argumentos={
                        "titulo": titulo,
                        "descricao": descricao
                    }
                )

        # =====================================================
        # REMOVER PRAZO
        # =====================================================

        padroes_remover_prazo = [
            r"remova o prazo da tarefa (.+)",
            r"remove o prazo da tarefa (.+)",
            r"tire o prazo da tarefa (.+)",
            r"deixe a tarefa (.+) sem prazo"
        ]

        for padrao in padroes_remover_prazo:

            match = re.search(
                padrao,
                texto,
                flags=re.IGNORECASE
            )

            if match:
                titulo = (
                    AraAgent._limpar_titulo(
                        match.group(1)
                    )
                )

                return AgentDecision(
                    acao=TipoAcao.EXECUTAR,
                    ferramenta="editar_tarefa",
                    argumentos={
                        "titulo": titulo,
                        "remover_data_limite": True
                    }
                )

        # =====================================================
        # ALTERAR PRAZO
        # =====================================================

        padroes_prazo = [
            r"altere o prazo da tarefa (.+?) para (.+)",
            r"mude o prazo da tarefa (.+?) para (.+)",
            r"defina o prazo da tarefa (.+?) para (.+)",
            r"coloque o prazo da tarefa (.+?) para (.+)",
            r"jogue a tarefa (.+?) para (.+)",
            r"joga a tarefa (.+?) para (.+)"
        ]

        for padrao in padroes_prazo:

            match = re.search(
                padrao,
                texto,
                flags=re.IGNORECASE
            )

            if match:

                titulo = (
                    AraAgent._limpar_titulo(
                        match.group(1)
                    )
                )

                texto_data = (
                    match.group(2)
                    .strip()
                )

                data_limite = (
                    NaturalTimeService.interpretar(
                        texto_data
                    )
                )

                if data_limite is None:
                    return AgentDecision(
                        acao=TipoAcao.CONVERSAR
                    )

                return AgentDecision(
                    acao=TipoAcao.EXECUTAR,
                    ferramenta="editar_tarefa",
                    argumentos={
                        "titulo": titulo,
                        "data_limite":
                            data_limite.isoformat()
                    }
                )

        # =====================================================
        # CRIAR TAREFA
        # =====================================================

        gatilhos_criar = [
            "quero criar uma tarefa",
            "quero adicionar uma tarefa",
            "gostaria de criar uma tarefa",
            "gostaria de adicionar uma tarefa",
            "cria uma tarefa",
            "crie uma tarefa",
            "criar uma tarefa",
            "adiciona uma tarefa",
            "adicione uma tarefa",
            "adicionar uma tarefa"
        ]

        for gatilho in gatilhos_criar:

            if gatilho in texto:

                indice = texto.find(
                    gatilho
                )

                inicio = (
                        indice
                        + len(gatilho)
                )

                conteudo_tarefa = mensagem[
                    inicio:
                ].strip()

                # =================================================
                # DETECTA DATA/HORA
                # =================================================

                data_limite = (
                    NaturalTimeService.interpretar(
                        conteudo_tarefa
                    )
                )

                # =================================================
                # REMOVE DATA/HORA DO TÍTULO
                # =================================================

                titulo = (
                    NaturalTimeService
                    .remover_tempo_do_texto(
                        conteudo_tarefa
                    )
                )

                # =================================================
                # LIMPA TÍTULO
                # =================================================

                titulo = (
                    AraAgent._limpar_titulo(
                        titulo
                    )
                )

                # =================================================
                # NORMALIZAÇÃO DO TÍTULO
                #
                # Exemplos:
                #
                # "quero criar uma tarefa chamada estudar Java"
                #     -> "estudar Java"
                #
                # "estudar Java para amanhã às 19h"
                #     -> "estudar Java"
                # =================================================

                titulo = re.sub(
                    r"(?i)^\s*(?:"
                    r"chamada|chamado|"
                    r"com\s+o\s+nome\s+de|"
                    r"com\s+nome\s+de"
                    r")\s+",
                    "",
                    titulo
                ).strip()

                # remover_tempo_do_texto pode deixar o conector
                # imediatamente anterior à expressão temporal.
                if data_limite is not None:
                    titulo = re.sub(
                        r"(?i)\s+(?:"
                        r"para|pra|"
                        r"em|no|na|"
                        r"às|as"
                        r")\s*$",
                        "",
                        titulo
                    ).strip()

                titulo = (
                    AraAgent._limpar_titulo(
                        titulo
                    )
                )

                # =================================================
                # PROTEÇÃO CONTRA TÍTULO RESIDUAL
                #
                # Exemplo:
                # "crie uma tarefa para amanhã às 15h"
                #
                # Depois da remoção da data pode sobrar somente
                # "para". Isso não representa um título válido.
                # =================================================

                titulo_normalizado = (
                    re.sub(
                        r"\s+",
                        " ",
                        titulo.lower()
                    )
                    .strip(" ,.;:-")
                )

                apenas_conectores = bool(
                    re.fullmatch(
                        r"(?:"
                        r"para|pra|"
                        r"em|no|na|"
                        r"a|o|as|às|"
                        r"ao|aos|"
                        r"de|do|da|dos|das"
                        r")"
                        r"(?:\s+(?:"
                        r"para|pra|"
                        r"em|no|na|"
                        r"a|o|as|às|"
                        r"ao|aos|"
                        r"de|do|da|dos|das"
                        r"))*",
                        titulo_normalizado
                    )
                )

                if (
                        not titulo_normalizado
                        or apenas_conectores
                ):
                    return AgentDecision(
                        acao=TipoAcao.CONVERSAR
                    )

                # =================================================
                # PRIORIDADE
                # =================================================

                prioridade = (
                    AraAgent._detectar_prioridade(
                        mensagem
                    )
                )

                # =================================================
                # DEBUG
                # =================================================

                print(
                    "\n===== TAREFA DEBUG ====="
                )

                print(
                    "Texto:",
                    conteudo_tarefa
                )

                print(
                    "Data detectada:",
                    data_limite
                )

                print(
                    "Título final:",
                    titulo
                )

                print(
                    "Prioridade:",
                    prioridade
                )

                print(
                    "========================\n"
                )

                if titulo:
                    return AgentDecision(
                        acao=TipoAcao.EXECUTAR,
                        ferramenta="criar_tarefa",
                        argumentos={
                            "titulo": titulo,
                            "descricao": None,
                            "prioridade": prioridade,
                            "data_limite": (
                                data_limite.isoformat()
                                if data_limite
                                else None
                            )
                        }
                    )

        # =====================================================
        # INICIAR
        # =====================================================

        gatilhos_iniciar = [
            "inicia a tarefa",
            "inicie a tarefa",
            "começa a tarefa",
            "comece a tarefa",
            "começar tarefa"
        ]

        for gatilho in gatilhos_iniciar:

            if gatilho in texto:

                titulo = texto.split(
                    gatilho,
                    1
                )[1].strip()

                titulo = re.sub(
                    r"^(de|do|da)\s+",
                    "",
                    titulo
                )

                titulo = (
                    AraAgent._limpar_titulo(
                        titulo
                    )
                )

                if titulo:
                    return AgentDecision(
                        acao=TipoAcao.EXECUTAR,
                        ferramenta="iniciar_tarefa",
                        argumentos={
                            "titulo": titulo
                        }
                    )

        # =====================================================
        # REABRIR
        # =====================================================

        gatilhos_reabrir = [
            "refaz a tarefa",
            "refaça a tarefa",
            "refazer tarefa",
            "reabre a tarefa",
            "reabra a tarefa",
            "reabrir tarefa",
            "quero fazer de novo a tarefa"
        ]

        for gatilho in gatilhos_reabrir:

            if gatilho in texto:

                titulo = texto.split(
                    gatilho,
                    1
                )[1].strip()

                titulo = re.sub(
                    r"^(de|do|da)\s+",
                    "",
                    titulo
                )

                titulo = (
                    AraAgent._limpar_titulo(
                        titulo
                    )
                )

                if titulo:
                    return AgentDecision(
                        acao=TipoAcao.EXECUTAR,
                        ferramenta="reabrir_tarefa",
                        argumentos={
                            "titulo": titulo
                        }
                    )

        # =====================================================
        # CONCLUIR
        # =====================================================

        gatilhos_concluir = [
            "conclui a tarefa",
            "conclua a tarefa",
            "finaliza a tarefa",
            "finalize a tarefa",
            "termina a tarefa",
            "terminei a tarefa"
        ]

        for gatilho in gatilhos_concluir:

            if gatilho in texto:

                titulo = texto.split(
                    gatilho,
                    1
                )[1].strip()

                titulo = re.sub(
                    r"^(de|do|da)\s+",
                    "",
                    titulo
                )

                titulo = (
                    AraAgent._limpar_titulo(
                        titulo
                    )
                )

                if titulo:
                    return AgentDecision(
                        acao=TipoAcao.EXECUTAR,
                        ferramenta="concluir_tarefa",
                        argumentos={
                            "titulo": titulo
                        }
                    )

        # =====================================================
        # CANCELAR
        # =====================================================

        gatilhos_cancelar = [
            "cancela a tarefa",
            "cancele a tarefa",
            "cancelar tarefa",
            "remove a tarefa"
        ]

        for gatilho in gatilhos_cancelar:

            if gatilho in texto:

                titulo = texto.split(
                    gatilho,
                    1
                )[1].strip()

                titulo = re.sub(
                    r"^(de|do|da)\s+",
                    "",
                    titulo
                )

                titulo = (
                    AraAgent._limpar_titulo(
                        titulo
                    )
                )

                if titulo:
                    return AgentDecision(
                        acao=TipoAcao.EXECUTAR,
                        ferramenta="cancelar_tarefa",
                        argumentos={
                            "titulo": titulo
                        }
                    )

        return None

    @staticmethod
    def _resolver_lembrete_contextual(
            mensagem: str,
            db: Session | None,
            id_usuario: int | None,
            id_conversa: int | None
    ):
        """
        Resolve referências contextuais de lembrete.

        Prioridade:
        1. entidade contextual da conversa, se ainda estiver ativa;
        2. ultimo_lembrete_id do contexto operacional, se ativo;
        3. lembrete pendente mais recente do usuário.

        Lembretes CONCLUIDOS ou CANCELADOS não podem assumir
        uma referência genérica como "esse lembrete".
        """

        if (
                db is None
                or id_usuario is None
                or id_conversa is None
        ):
            return None

        # ====================================================
        # VALIDAÇÃO CENTRAL
        # ====================================================

        def lembrete_ativo(lembrete):

            if lembrete is None:
                return False

            if lembrete.id_usuario != id_usuario:
                return False

            status = (
                lembrete.status.value
                if hasattr(lembrete.status, "value")
                else str(lembrete.status)
            )

            return status not in {
                "CONCLUIDA",
                "CANCELADA"
            }

        # ====================================================
        # 1. ENTIDADE CONTEXTUAL
        # ====================================================

        entidade = (
            EntidadeContextualService
            .resolver_referencia_generica(
                db=db,
                id_usuario=id_usuario,
                id_conversa=id_conversa,
                texto=mensagem,
                tipo_entidade="LEMBRETE"
            )
        )

        if entidade is not None:

            try:
                lembrete = (
                    LembreteService.buscar_por_id(
                        db,
                        entidade.id_entidade
                    )
                )

                if lembrete_ativo(lembrete):
                    return lembrete

            except ValueError:
                pass

        # ====================================================
        # 2. CONTEXTO OPERACIONAL
        # ====================================================

        try:

            id_ultimo = (
                ContextoAgenteService
                .obter_ultimo_lembrete_id(
                    db=db,
                    id_usuario=id_usuario,
                    id_conversa=id_conversa
                )
            )

            if id_ultimo is not None:

                lembrete = (
                    LembreteService.buscar_por_id(
                        db,
                        id_ultimo
                    )
                )

                if lembrete_ativo(lembrete):
                    return lembrete

        except (ValueError, AttributeError):
            pass

        # ====================================================
        # 3. FALLBACK:
        # LEMBRETE ATIVO MAIS RECENTE
        # ====================================================

        lembretes = (
            LembreteService.listar(
                db,
                id_usuario
            )
        )

        ativos = [
            item
            for item in lembretes
            if lembrete_ativo(item)
        ]

        if not ativos:
            return None

        return max(
            ativos,
            key=lambda item: item.id_lembrete
        )

    @staticmethod
    def _detectar_acao_contextual_lembrete(
            mensagem: str,
            db: Session | None,
            id_usuario: int | None,
            id_conversa: int | None
    ) -> AgentDecision | None:

        texto = mensagem.lower().strip()

        # Só tenta resolver contexto se claramente
        # estivermos falando de lembrete.
        referencias = [
            "lembrete",
            "lembretes",
            "ele",
            "esse lembrete",
            "essa lembrete",
            "este lembrete",
            "esta lembrete"
        ]

        if not any(
                termo in texto
                for termo in referencias
        ):
            return None

        lembrete = (
            AraAgent._resolver_lembrete_contextual(
                mensagem=mensagem,
                db=db,
                id_usuario=id_usuario,
                id_conversa=id_conversa
            )
        )

        if lembrete is None:
            return None

        titulo = lembrete.titulo

        # =====================================================
        # EDITAR DATA / HORÁRIO
        # =====================================================

        if any(
                termo in texto
                for termo in [
                    "adie",
                    "adiar",
                    "mude",
                    "mudar",
                    "altere",
                    "alterar",
                    "remarque",
                    "remarcar",
                    "reagende",
                    "reagendar"
                ]
        ):
            # Captura a parte temporal da mensagem.
            # A própria tool resolve data completa ou apenas horário.
            temporal = texto

            return AgentDecision(
                acao=TipoAcao.EXECUTAR,
                ferramenta="editar_lembrete",
                argumentos={
                    "id_lembrete": lembrete.id_lembrete,
                    "titulo": titulo,
                    "nova_data_hora": temporal
                }
            )

        # =====================================================
        # CONCLUIR
        # =====================================================

        if any(
                termo in texto
                for termo in [
                    "conclui",
                    "conclua",
                    "concluir",
                    "finaliza",
                    "finalize",
                    "terminei"
                ]
        ):
            return AgentDecision(
                acao=TipoAcao.EXECUTAR,
                ferramenta="concluir_lembrete",
                argumentos={
                    "id_lembrete": lembrete.id_lembrete,
                    "titulo": titulo
                }
            )

        # =====================================================
        # CANCELAR
        # =====================================================

        if any(
                termo in texto
                for termo in [
                    "cancela",
                    "cancele",
                    "cancelar",
                    "apaga",
                    "apague"
                ]
        ):
            return AgentDecision(
                acao=TipoAcao.EXECUTAR,
                ferramenta="cancelar_lembrete",
                argumentos={
                    "id_lembrete": lembrete.id_lembrete,
                    "titulo": titulo
                }
            )

        return None


