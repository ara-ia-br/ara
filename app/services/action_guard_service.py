import re
import unicodedata
from dataclasses import dataclass


@dataclass
class ResultadoActionGuard:
    operacional: bool
    dominio: str | None = None
    operacao: str | None = None
    resposta: str | None = None


class ActionGuardService:
    """
    Barreira de segurança entre o Agent determinístico
    e o fallback conversacional da IA.

    O Action Guard NÃO executa ferramentas.

    Sua responsabilidade é impedir que uma solicitação
    operacional não mapeada pelo Agent seja enviada ao LLM
    como se fosse apenas conversa.
    """

    _VERBOS_OPERACIONAIS = {
        "criar": "CRIAR",
        "crie": "CRIAR",
        "adicionar": "CRIAR",
        "adicione": "CRIAR",
        "registrar": "CRIAR",
        "registre": "CRIAR",
        "salvar": "CRIAR",
        "salve": "CRIAR",
        "agendar": "CRIAR",
        "agende": "CRIAR",
        "marcar": "CRIAR",
        "marque": "CRIAR",

        "editar": "EDITAR",
        "edite": "EDITAR",
        "alterar": "EDITAR",
        "altere": "EDITAR",
        "mudar": "EDITAR",
        "mude": "EDITAR",
        "atualizar": "EDITAR",
        "atualize": "EDITAR",
        "renomear": "EDITAR",
        "renomeie": "EDITAR",
        "adiar": "EDITAR",
        "adie": "EDITAR",

        "concluir": "CONCLUIR",
        "conclua": "CONCLUIR",
        "finalizar": "CONCLUIR",
        "finalize": "CONCLUIR",
        "terminar": "CONCLUIR",
        "termine": "CONCLUIR",

        "iniciar": "INICIAR",
        "inicie": "INICIAR",
        "comecar": "INICIAR",
        "comece": "INICIAR",

        "cancelar": "CANCELAR",
        "cancele": "CANCELAR",

        "excluir": "EXCLUIR",
        "exclua": "EXCLUIR",
        "deletar": "EXCLUIR",
        "delete": "EXCLUIR",
        "apagar": "EXCLUIR",
        "apague": "EXCLUIR",
        "remover": "EXCLUIR",
        "remova": "EXCLUIR",

        "reabrir": "REABRIR",
        "reabra": "REABRIR",

        "enviar": "ENVIAR",
        "envie": "ENVIAR",
    }

    _DOMINIOS = {
        "TAREFA": {
            "tarefa",
            "tarefas",
        },

        "LEMBRETE": {
            "lembrete",
            "lembretes",
        },

        "EMAIL": {
            "email",
            "emails",
            "e-mail",
            "e-mails",
        },

        "CALENDARIO": {
            "calendario",
            "agenda",
            "evento",
            "eventos",
            "compromisso",
            "compromissos",
        },
    }

    @staticmethod
    def _normalizar(texto: str) -> str:

        texto = str(
            texto or ""
        ).lower().strip()

        texto = unicodedata.normalize(
            "NFD",
            texto
        )

        texto = "".join(
            caractere
            for caractere in texto
            if unicodedata.category(
                caractere
            ) != "Mn"
        )

        texto = re.sub(
            r"\s+",
            " ",
            texto
        )

        return texto

    @classmethod
    def _detectar_operacao(
        cls,
        texto: str
    ) -> str | None:

        for verbo, operacao in (
            cls._VERBOS_OPERACIONAIS.items()
        ):

            if re.search(
                rf"\b{re.escape(verbo)}\b",
                texto
            ):
                return operacao

        return None

    @classmethod
    def _detectar_dominio(
        cls,
        texto: str
    ) -> str | None:

        for dominio, termos in (
            cls._DOMINIOS.items()
        ):

            for termo in termos:

                termo_normalizado = (
                    cls._normalizar(
                        termo
                    )
                )

                if re.search(
                    rf"\b"
                    rf"{re.escape(termo_normalizado)}"
                    rf"\b",
                    texto
                ):
                    return dominio

        return None

    @classmethod
    def analisar(
        cls,
        mensagem: str
    ) -> ResultadoActionGuard:

        texto = cls._normalizar(
            mensagem
        )

        if not texto:
            return ResultadoActionGuard(
                operacional=False
            )

        padroes_instrucionais = (
            r"^como\s+",
            r"^como\s+(?:eu\s+)?(?:posso|faco|fazer)\b",
            r"^me\s+ensine\s+",
            r"^me\s+explique\s+",
            r"^explique\s+",

            # Consultas iniciadas por "qual".
            #
            # Exemplos:
            # "qual é a prioridade dela?"
            # "qual seria o prazo dela?"
            #
            # Não devem ser interpretadas como mutação.
            r"^qual\s+(?:e|seria)\s+",

            r"^o\s+que\s+(?:e|significa)\s+",
            r"^posso\s+",
            r"^eu\s+consigo\s+",
        )

        if any(
            re.search(
                padrao,
                texto
            )
            for padrao in padroes_instrucionais
        ):
            return ResultadoActionGuard(
                operacional=False
            )

        operacao = cls._detectar_operacao(
            texto
        )

        dominio = cls._detectar_dominio(
            texto
        )

        if (
            operacao is None
            or dominio is None
        ):
            return ResultadoActionGuard(
                operacional=False
            )

        respostas = {
            "TAREFA": (
                "Entendi que você quer realizar uma ação "
                "em uma tarefa, mas não consegui identificar "
                "com segurança todos os dados necessários "
                "para executá-la. Pode especificar melhor "
                "a tarefa e o que deseja fazer?"
            ),

            "LEMBRETE": (
                "Entendi que você quer realizar uma ação "
                "em um lembrete, mas não consegui identificar "
                "com segurança todos os dados necessários "
                "para executá-la. Pode especificar melhor "
                "o lembrete e o que deseja fazer?"
            ),

            "EMAIL": (
                "Entendi que você quer realizar uma ação "
                "envolvendo e-mail, mas essa operação não "
                "foi confirmada por uma ferramenta disponível."
            ),

            "CALENDARIO": (
                "Entendi que você quer realizar uma ação "
                "envolvendo agenda ou calendário, mas essa "
                "operação não foi confirmada por uma "
                "ferramenta disponível."
            ),
        }

        return ResultadoActionGuard(
            operacional=True,
            dominio=dominio,
            operacao=operacao,
            resposta=respostas.get(
                dominio,
                (
                    "Entendi que você quer executar uma ação, "
                    "mas não consegui confirmá-la com segurança."
                )
            )
        )

    @classmethod
    def analisar_contextual(
        cls,
        mensagem: str,
        dominio_contextual: str | None = None
    ) -> ResultadoActionGuard:
        """
        Segunda barreira do Action Guard.

        É utilizada somente depois que:

        1. o Agent não executou uma Tool;
        2. o Action Guard explícito não identificou
           domínio + operação;
        3. o ChatService encontrou contexto operacional
           suficiente para determinar o domínio.

        O método NÃO executa nenhuma ferramenta.
        """

        texto = cls._normalizar(
            mensagem
        )

        if (
            not texto
            or dominio_contextual is None
        ):
            return ResultadoActionGuard(
                operacional=False
            )

        dominio_contextual = (
            str(dominio_contextual)
            .upper()
            .strip()
        )

        if dominio_contextual not in {
            "TAREFA",
            "LEMBRETE",
            "EMAIL",
            "CALENDARIO",
        }:
            return ResultadoActionGuard(
                operacional=False
            )

        # =====================================================
        # EXCLUSÕES CONVERSACIONAIS / INSTRUCIONAIS
        # =====================================================

        padroes_instrucionais = (
            r"^como\s+",
            r"^como\s+(?:eu\s+)?(?:posso|faco|fazer)\b",
            r"^me\s+ensine\s+",
            r"^me\s+explique\s+",
            r"^explique\s+",
            r"^qual\s+(?:e|seria)\s+a\s+forma\s+",
            r"^qual\s+(?:e|seria)\s+o\s+jeito\s+",
            r"^o\s+que\s+(?:e|significa)\s+",
            r"^posso\s+",
            r"^eu\s+consigo\s+",
        )

        if any(
            re.search(
                padrao,
                texto
            )
            for padrao in padroes_instrucionais
        ):
            return ResultadoActionGuard(
                operacional=False
            )

        # =====================================================
        # OPERAÇÃO JÁ CONHECIDA
        # =====================================================

        # =====================================================
        # QUERY GUARD — CONSULTAS NÃO SÃO MUTAÇÕES
        # =====================================================
        #
        # Esta verificação precisa acontecer ANTES de
        # _detectar_operacao().
        #
        # Caso contrário, palavras de domínio como
        # "prioridade" podem fazer uma pergunta ser
        # interpretada como edição.
        #
        # Exemplos bloqueados aqui:
        #
        # "qual é a prioridade dela?"
        # "qual seria a prioridade dela?"
        # "qual é o prazo dela?"
        # "que prioridade ela tem?"
        # "quando ela vence?"
        # "ela está marcada para que horas?"

        padroes_consulta = (
            r"^qual\s+",
            r"^que\s+prioridade\b",
            r"^quando\s+",
            r"^quanto\s+",
            r"^onde\s+",
            r"^quem\s+",
            r"^ela\s+esta\b",
            r"^ele\s+esta\b",
        )

        if any(
            re.search(
                padrao,
                texto
            )
            for padrao in padroes_consulta
        ):
            return ResultadoActionGuard(
                operacional=False
            )

        operacao = cls._detectar_operacao(
            texto
        )

        # =====================================================
        # VERBOS CONTEXTUAIS ADICIONAIS
        # =====================================================
        #
        # "coloque ela..."
        # "coloca ela..."
        #
        # Esses verbos são considerados edição somente dentro
        # de um domínio contextual já determinado.

        if operacao is None:

            if re.search(
                r"\b(?:colocar|coloque|coloca)\b",
                texto
            ):
                operacao = "EDITAR"

        # =====================================================
        # CONTINUAÇÃO DE PRIORIDADE
        # =====================================================

        if (
            operacao is None
            and dominio_contextual == "TAREFA"
        ):

            # =================================================
            # CONSULTA SOBRE PRIORIDADE != EDIÇÃO
            # =================================================
            #
            # Exemplos:
            #
            # "qual é a prioridade dela?"
            # "qual seria a prioridade dela?"
            #
            # A presença simultânea de "prioridade" e "dela"
            # não significa que o usuário queira alterar a
            # tarefa.

            consulta_prioridade = bool(
                re.search(
                    r"^(?:"
                    r"qual\\s+(?:e|seria)"
                    r"|qual\\s+prioridade"
                    r"|que\\s+prioridade"
                    r"|qual\\s+e"
                    r")\\b",
                    texto
                )
            )

            if consulta_prioridade:

                return ResultadoActionGuard(
                    operacional=False
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
                    texto
                )
            )

            possui_continuacao = bool(
                re.search(
                    r"\b(?:"
                    r"tambem"
                    r"|ela"
                    r"|dela"
                    r"|essa"
                    r"|dessa"
                    r"|esta"
                    r"|desta"
                    r")\b",
                    texto
                )
            )

            if (
                possui_prioridade
                and possui_continuacao
            ):
                operacao = "EDITAR"

        if operacao is None:
            return ResultadoActionGuard(
                operacional=False
            )

        respostas = {
            "TAREFA": (
                "Entendi que você quer realizar uma ação "
                "na tarefa em contexto, mas não consegui "
                "confirmar a execução com segurança. "
                "Pode especificar melhor o que deseja alterar?"
            ),

            "LEMBRETE": (
                "Entendi que você quer realizar uma ação "
                "no lembrete em contexto, mas não consegui "
                "confirmar a execução com segurança. "
                "Pode especificar melhor o que deseja fazer?"
            ),

            "EMAIL": (
                "Entendi que você quer realizar uma ação "
                "envolvendo e-mail, mas essa operação não "
                "foi confirmada por uma ferramenta disponível."
            ),

            "CALENDARIO": (
                "Entendi que você quer realizar uma ação "
                "envolvendo agenda ou calendário, mas essa "
                "operação não foi confirmada por uma "
                "ferramenta disponível."
            ),
        }

        return ResultadoActionGuard(
            operacional=True,
            dominio=dominio_contextual,
            operacao=operacao,
            resposta=respostas[
                dominio_contextual
            ]
        )
