import json
import re

from app.services.lembrete_service import (
    LembreteService
)

from datetime import timedelta

from sqlalchemy.orm import Session

from app.ai.engine import ai_engine

from app.agent.intent import (
    AgentDecision,
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


class JarvisAgent:

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
            JarvisAgent
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
            JarvisAgent._detectar_acao_tarefa(
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
            JarvisAgent
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
        # 3. AÇÕES DE LEMBRETE
        # =====================================================

        decisao_lembrete = (
            JarvisAgent._detectar_acao_lembrete(
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
            JarvisAgent._detectar_lembrete(
                mensagem
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
        # 5. FALLBACK VIA IA
        # =====================================================

        prompt = f"""
Você é o módulo de decisão do JARVIS.

Sua função é determinar se a mensagem do usuário
requer apenas uma resposta normal ou se deve
executar uma ferramenta.

CONTEXTO TEMPORAL OFICIAL:

{contexto_temporal}

A data e hora acima são a referência temporal oficial.

Ao interpretar expressões como:

- hoje
- amanhã
- depois de amanhã
- ontem
- segunda
- terça
- quarta
- quinta
- sexta
- sábado
- domingo
- horários relativos

use obrigatoriamente o contexto temporal informado.

Ferramentas disponíveis:

{ferramentas}

Mensagem do usuário:

{mensagem}

Responda SOMENTE com JSON válido.

Para conversa normal:

{{
    "acao": "CONVERSAR",
    "ferramenta": null,
    "argumentos": {{}}
}}

Para executar ferramenta:

{{
    "acao": "EXECUTAR",
    "ferramenta": "nome_da_ferramenta",
    "argumentos": {{}}
}}

Nunca escolha uma ferramenta que não esteja disponível.

Não escreva explicações.
Não use markdown.
Não use blocos de código.
Retorne exclusivamente JSON válido.
"""

        resposta = ai_engine.gerar_resposta(
            [
                {
                    "role": "system",
                    "content": (
                        "Você é um classificador de "
                        "intenções e ferramentas. "
                        "Retorne exclusivamente JSON válido."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        print(
            "\n===== AGENT DEBUG ====="
        )

        print(
            "Ferramentas:",
            ferramentas
        )

        print(
            "Resposta do modelo:"
        )

        print(
            resposta
        )

        print(
            "=======================\n"
        )

        return JarvisAgent._interpretar(
            resposta
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
    # DETECTAR LEMBRETE
    # =========================================================

    @staticmethod
    def _detectar_lembrete(
        mensagem: str
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
            r"(?i)\bjarvis\b[,\s]*",
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
            JarvisAgent._limpar_titulo(
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
                    JarvisAgent._limpar_titulo(
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
                    JarvisAgent._limpar_titulo(
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
            return None

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
        # RESOLVE REFERÊNCIA
        # =====================================================

        tarefa = (
            JarvisAgent._resolver_tarefa_contextual(
                mensagem=mensagem,
                db=db,
                id_usuario=id_usuario,
                id_conversa=id_conversa
            )
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
            "passe para"
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
                JarvisAgent._detectar_prioridade(
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
                    JarvisAgent._limpar_titulo(
                        match.group(1)
                    )
                )

                novo_titulo = (
                    JarvisAgent._limpar_titulo(
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
                    JarvisAgent._limpar_titulo(
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
                    JarvisAgent._limpar_titulo(
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
                    JarvisAgent._limpar_titulo(
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
                    JarvisAgent._limpar_titulo(
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
            "cria uma tarefa",
            "crie uma tarefa",
            "adiciona uma tarefa",
            "adicione uma tarefa"
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
                    JarvisAgent._limpar_titulo(
                        titulo
                    )
                )

                # =================================================
                # PRIORIDADE
                # =================================================

                prioridade = (
                    JarvisAgent._detectar_prioridade(
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
                    JarvisAgent._limpar_titulo(
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
                    JarvisAgent._limpar_titulo(
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
                    JarvisAgent._limpar_titulo(
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
                    JarvisAgent._limpar_titulo(
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

        if (
                db is None
                or id_usuario is None
                or id_conversa is None
        ):
            return None

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

        if entidade is None:
            return None

        try:

            lembrete = (
                LembreteService.buscar_por_id(
                    db,
                    entidade.id_entidade
                )
            )

        except ValueError:
            return None

        if lembrete.id_usuario != id_usuario:
            return None

        return lembrete

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
            "este lembrete"
        ]

        if not any(
                termo in texto
                for termo in referencias
        ):
            return None

        lembrete = (
            JarvisAgent._resolver_lembrete_contextual(
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
                    "titulo": titulo
                }
            )

        return None