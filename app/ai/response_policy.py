import re
import unicodedata


class ResponsePolicy:

    # =========================================================
    # NORMALIZAÇÃO
    # =========================================================

    @staticmethod
    def _normalizar(texto: str) -> str:

        texto = texto or ""

        texto = unicodedata.normalize(
            "NFD",
            texto
        )

        texto = "".join(
            caractere
            for caractere in texto
            if unicodedata.category(caractere) != "Mn"
        )

        return texto.lower().strip()


    # =========================================================
    # DETECTAR DOMÍNIO
    # =========================================================

    @staticmethod
    def _detectar_dominio(
        mensagem_usuario: str,
        resposta: str
    ) -> str | None:

        texto = ResponsePolicy._normalizar(
            f"{mensagem_usuario} {resposta}"
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
    # DETECTAR CONFIRMAÇÃO OPERACIONAL
    # =========================================================

    @staticmethod
    def _possui_confirmacao_operacional(
        resposta: str
    ) -> bool:

        texto = ResponsePolicy._normalizar(
            resposta
        )

        padroes = [

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
            r")\b",

            r"\b(?:tarefa|lembrete)\b"
            r".{0,100}"
            r"\b(?:"
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
            r")\b",

            r"\b(?:ja ha|ja existe|encontrei|localizei)\b"
            r".{0,100}"
            r"\b(?:tarefa|lembrete)\b",

            r"\b(?:tarefa|lembrete)\b"
            r".{0,100}"
            r"\b(?:"
            r"ja existe|"
            r"ja esta cadastrado|"
            r"ja esta cadastrada"
            r")\b",
        ]

        return any(
            re.search(
                padrao,
                texto,
                flags=re.IGNORECASE
            ) is not None
            for padrao in padroes
        )


    # =========================================================
    # VALIDAR FALLBACK CONVERSACIONAL
    # =========================================================

    @staticmethod
    def validar_fallback(
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

        if not (
            ResponsePolicy
            ._possui_confirmacao_operacional(
                resposta
            )
        ):
            return resposta

        dominio = (
            ResponsePolicy
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