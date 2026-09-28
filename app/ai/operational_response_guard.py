import re
import unicodedata


class OperationalResponseGuard:

    # =========================================================
    # NORMALIZAÇÃO
    # =========================================================

    @staticmethod
    def _normalizar(
        texto: str | None
    ) -> str:

        texto = texto or ""

        texto = unicodedata.normalize(
            "NFD",
            str(texto)
        )

        texto = "".join(
            caractere
            for caractere in texto
            if unicodedata.category(
                caractere
            ) != "Mn"
        )

        return texto.lower().strip()

    # =========================================================
    # CONSULTA INFORMATIVA / CAPACIDADE
    # =========================================================

    @staticmethod
    def _eh_consulta_informativa(
        mensagem_usuario: str
    ) -> bool:

        texto = (
            OperationalResponseGuard
            ._normalizar(
                mensagem_usuario
            )
        )

        padroes = (
            # Conceito / definição
            r"^(?:o que e|oque e)\b",
            r"^o que significa\b",
            r"^para que serve\b",
            r"^como funciona\b",

            # Pergunta sobre capacidade
            (
                r"^(?:voce\s+)?"
                r"(?:consegue|pode|sabe)\s+"
                r"(?:criar|listar|consultar|editar|"
                r"cancelar|concluir|reabrir|iniciar|excluir)"
                r"\s+(?:tarefas?|lembretes?)\s*\??$"
            ),

            # Pergunta sobre recursos
            (
                r"^(?:quais|que)\s+"
                r"(?:funcoes|recursos|operacoes|acoes)"
                r".*\b(?:tarefas?|lembretes?)\b"
            ),

            # Pergunta instrucional
            (
                r"^como\s+(?:eu\s+)?"
                r"(?:posso|faco para)\b"
                r".*\b(?:tarefas?|lembretes?)\b"
            ),

            (
                r"^como\s+"
                r"(?:criar|listar|consultar|editar|"
                r"cancelar|concluir|reabrir|iniciar|excluir)"
                r".*\b(?:tarefas?|lembretes?)\b"
            ),
        )

        return any(
            re.search(
                padrao,
                texto
            ) is not None
            for padrao in padroes
        )

    # =========================================================
    # DETECTA DOMÍNIO
    # =========================================================

    @staticmethod
    def _detectar_dominio(
        mensagem_usuario: str,
        resposta: str
    ) -> str | None:

        texto = (
            OperationalResponseGuard
            ._normalizar(
                f"{mensagem_usuario} {resposta}"
            )
        )

        if re.search(
            r"\blembretes?\b",
            texto
        ):
            return "LEMBRETE"

        if re.search(
            r"\btarefas?\b",
            texto
        ):
            return "TAREFA"

        return None

    # =========================================================
    # CONFIRMAÇÃO EXPLÍCITA EM PRIMEIRA PESSOA
    # =========================================================

    @staticmethod
    def _possui_confirmacao_explicita(
        resposta: str
    ) -> bool:

        texto = (
            OperationalResponseGuard
            ._normalizar(
                resposta
            )
        )

        padrao = (
            r"\b(?:"
            r"criei|"
            r"agendei|"
            r"salvei|"
            r"registrei|"
            r"adicionei|"
            r"inclui|"
            r"cancelei|"
            r"conclui|"
            r"alterei|"
            r"atualizei|"
            r"editei|"
            r"exclui|"
            r"apaguei|"
            r"removi|"
            r"reabri|"
            r"iniciei"
            r")\b"
        )

        return (
            re.search(
                padrao,
                texto
            )
            is not None
        )

    # =========================================================
    # CONFIRMAÇÃO OPERACIONAL
    # =========================================================

    @staticmethod
    def _possui_confirmacao_operacional(
        resposta: str
    ) -> bool:

        texto = (
            OperationalResponseGuard
            ._normalizar(
                resposta
            )
        )

        # Confirmação forte em primeira pessoa.
        if (
            OperationalResponseGuard
            ._possui_confirmacao_explicita(
                resposta
            )
        ):
            return True

        padroes = (

            # Ex.:
            # "O lembrete foi criado."
            # "A tarefa ficou concluída."
            (
                r"\b(?:tarefa|lembrete)\b"
                r".{0,100}"
                r"\b(?:foi|ficou|esta)\s+"
                r"(?:"
                r"criado|criada|"
                r"agendado|agendada|"
                r"cancelado|cancelada|"
                r"concluido|concluida|"
                r"alterado|alterada|"
                r"atualizado|atualizada|"
                r"editado|editada|"
                r"excluido|excluida|"
                r"removido|removida|"
                r"reaberto|reaberta|"
                r"iniciado|iniciada"
                r")\b"
            ),

            # Ex.:
            # "Já existe uma tarefa..."
            (
                r"\b(?:ja ha|ja existe|encontrei|localizei)\b"
                r".{0,100}"
                r"\b(?:tarefa|lembrete)\b"
            ),

            (
                r"\b(?:tarefa|lembrete)\b"
                r".{0,100}"
                r"\b(?:"
                r"ja existe|"
                r"ja esta cadastrado|"
                r"ja esta cadastrada"
                r")\b"
            ),
        )

        return any(
            re.search(
                padrao,
                texto,
                flags=re.IGNORECASE
            ) is not None
            for padrao in padroes
        )

    # =========================================================
    # VALIDAÇÃO
    # =========================================================

    @staticmethod
    def validar(
        mensagem_usuario: str,
        resposta_modelo: str
    ) -> str:

        resposta = (
            resposta_modelo or ""
        ).strip()

        if not resposta:
            return (
                "Não consegui gerar uma resposta "
                "adequada agora."
            )

        # =====================================================
        # CONSULTA INFORMATIVA
        # =====================================================
        #
        # Perguntas como:
        #
        # "o que é um lembrete?"
        # "como funciona uma tarefa?"
        # "você consegue criar lembretes?"
        #
        # não são, por si só, pedidos para executar uma Tool.
        #
        # Porém, se o modelo responder com uma confirmação
        # explícita como "criei", ainda bloqueamos.
        # =====================================================

        if (
            OperationalResponseGuard
            ._eh_consulta_informativa(
                mensagem_usuario
            )
            and not (
                OperationalResponseGuard
                ._possui_confirmacao_explicita(
                    resposta
                )
            )
        ):
            return resposta

        # =====================================================
        # SEM CONFIRMAÇÃO OPERACIONAL
        # =====================================================

        if not (
            OperationalResponseGuard
            ._possui_confirmacao_operacional(
                resposta
            )
        ):
            return resposta

        # =====================================================
        # CONFIRMAÇÃO SEM TOOL
        # =====================================================

        dominio = (
            OperationalResponseGuard
            ._detectar_dominio(
                mensagem_usuario,
                resposta
            )
        )

        if dominio == "LEMBRETE":
            return (
                "Não consegui confirmar essa operação "
                "de lembrete no sistema. "
                "Tente novamente com o pedido de forma direta."
            )

        if dominio == "TAREFA":
            return (
                "Não consegui confirmar essa operação "
                "de tarefa no sistema. "
                "Tente novamente com o pedido de forma direta."
            )

        return (
            "Não consegui confirmar essa operação "
            "no sistema. Tente novamente."
        )
