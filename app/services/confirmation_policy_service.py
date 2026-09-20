class ConfirmationPolicyService:
    """
    Política central de confirmação operacional.

    Define quais ferramentas precisam de confirmação explícita
    antes de serem executadas.

    O ChatService não deve decidir individualmente quais ações
    são sensíveis. Essa responsabilidade fica centralizada aqui.
    """

    _POLITICAS = {
        "excluir_todos_lembretes": {
            "exige_confirmacao": True,
            "dominio": "LEMBRETE",
            "operacao": "EXCLUIR_TODOS",
            "descricao": (
                "Excluir todos os lembretes do usuário."
            ),
            "mensagem_confirmacao": (
                "Isso vai excluir todos os seus lembretes. "
                "As tarefas vinculadas serão mantidas. "
                "Tem certeza que deseja continuar?"
            ),
            "mensagem_cancelamento": (
                "Certo, não excluí nenhum lembrete."
            )
        }
    }

    @classmethod
    def obter(
        cls,
        ferramenta: str | None
    ) -> dict | None:

        if not ferramenta:
            return None

        politica = cls._POLITICAS.get(
            str(ferramenta)
        )

        if politica is None:
            return None

        return politica.copy()

    @classmethod
    def exige_confirmacao(
        cls,
        ferramenta: str | None
    ) -> bool:

        politica = cls.obter(
            ferramenta
        )

        if politica is None:
            return False

        return (
            politica.get(
                "exige_confirmacao"
            )
            is True
        )

    @classmethod
    def preparar(
        cls,
        ferramenta: str,
        argumentos: dict | None = None
    ) -> dict | None:
        """
        Retorna os dados necessários para registrar
        uma ação pendente.

        Retorna None quando a ferramenta não exige confirmação.
        """

        politica = cls.obter(
            ferramenta
        )

        if (
            politica is None
            or politica.get(
                "exige_confirmacao"
            )
            is not True
        ):
            return None

        return {
            "ferramenta": ferramenta,
            "argumentos": (
                dict(argumentos)
                if argumentos
                else {}
            ),
            "dominio":
                politica.get("dominio"),
            "operacao":
                politica.get("operacao"),
            "descricao":
                politica.get("descricao"),
            "mensagem_confirmacao":
                politica.get(
                    "mensagem_confirmacao"
                ),
            "mensagem_cancelamento":
                politica.get(
                    "mensagem_cancelamento"
                )
        }
