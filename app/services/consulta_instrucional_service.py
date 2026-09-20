import re
import unicodedata


class ConsultaInstrucionalService:
    """
    Detecta perguntas sobre COMO usar funcionalidades operacionais
    da A.R.A.

    Uma consulta instrucional nunca representa autorização para
    executar a operação mencionada.
    """

    @staticmethod
    def _normalizar(texto: str) -> str:

        texto = (
            texto
            .lower()
            .strip()
        )

        texto = "".join(
            caractere
            for caractere in unicodedata.normalize(
                "NFD",
                texto
            )
            if unicodedata.category(
                caractere
            ) != "Mn"
        )

        return re.sub(
            r"\s+",
            " ",
            texto
        ).strip()


    @classmethod
    def analisar(
        cls,
        mensagem: str
    ) -> dict | None:

        if not mensagem:
            return None

        texto = cls._normalizar(
            mensagem
        )

        # =====================================================
        # ESTRUTURA INSTRUCIONAL
        # =====================================================

        padroes_instrucionais = (
            r"^como\b",
            r"^como\s+eu\b",
            r"^como\s+posso\b",
            r"^me\s+ensine\b",
            r"^me\s+explique\b",
            r"^me\s+mostre\s+como\b",
            r"^me\s+diga\s+como\b",
            r"^quero\s+saber\s+como\b",
            r"^gostaria\s+de\s+saber\s+como\b",
            r"^pode\s+me\s+explicar\s+como\b",
            r"^poderia\s+me\s+explicar\s+como\b",
            r"^posso\b",
            r"^eu\s+consigo\b",
            r"^qual\s+(?:e|seria)\s+"
            r"(?:a\s+)?(?:forma|maneira)\b",
            r"^qual\s+(?:e|seria)\s+"
            r"(?:o\s+)?jeito\b",
        )

        eh_instrucional = any(
            re.search(
                padrao,
                texto
            )
            for padrao in padroes_instrucionais
        )

        if not eh_instrucional:
            return None

        # =====================================================
        # DOMÍNIO
        # =====================================================

        if re.search(
            r"\blembretes?\b",
            texto
        ):
            dominio = "LEMBRETE"

        elif re.search(
            r"\btarefas?\b",
            texto
        ):
            dominio = "TAREFA"

        else:
            return None

        # =====================================================
        # OPERAÇÃO
        # =====================================================

        exclusao = bool(
            re.search(
                r"\b(?:"
                r"excluir|excluo|exclui|"
                r"apagar|apago|apaga|"
                r"deletar|deleto|deleta|"
                r"remover|removo|remove"
                r")\b",
                texto
            )
        )

        totalidade = bool(
            re.search(
                r"\b(?:todos|todas)\b",
                texto
            )
        )

        if (
            dominio == "LEMBRETE"
            and exclusao
            and totalidade
        ):
            return {
                "instrucional": True,
                "dominio": "LEMBRETE",
                "operacao": "EXCLUIR_TODOS",
                "resposta": (
                    "Para excluir todos os seus lembretes na A.R.A., "
                    'diga "exclua todos os meus lembretes". '
                    "Antes de remover qualquer lembrete, "
                    "eu vou pedir sua confirmação. "
                    "As tarefas vinculadas serão mantidas."
                )
            }

        if re.search(
            r"\b(?:criar|crio|cria|adicionar|adiciono|adiciona)\b",
            texto
        ):

            if dominio == "TAREFA":
                resposta = (
                    "Para criar uma tarefa na A.R.A., diga algo como "
                    '"crie uma tarefa chamada estudar banco de dados".'
                )
            else:
                resposta = (
                    "Para criar um lembrete na A.R.A., diga algo como "
                    '"crie um lembrete para estudar às 19h".'
                )

            return {
                "instrucional": True,
                "dominio": dominio,
                "operacao": "CRIAR",
                "resposta": resposta
            }

        if re.search(
            r"\b(?:listar|listo|lista|ver|consultar|consulto)\b",
            texto
        ):

            if dominio == "TAREFA":
                resposta = (
                    'Para consultar suas tarefas, diga '
                    '"liste minhas tarefas".'
                )
            else:
                resposta = (
                    'Para consultar seus lembretes, diga '
                    '"liste meus lembretes".'
                )

            return {
                "instrucional": True,
                "dominio": dominio,
                "operacao": "LISTAR",
                "resposta": resposta
            }

        if re.search(
            r"\b(?:concluir|concluo|conclui|finalizar|finalizo)\b",
            texto
        ):

            if dominio == "TAREFA":
                resposta = (
                    "Para concluir uma tarefa na A.R.A., "
                    'diga "conclua a tarefa" seguido do nome dela.'
                )
            else:
                resposta = (
                    "Para concluir um lembrete na A.R.A., "
                    'diga "conclua o lembrete" seguido do nome dele.'
                )

            return {
                "instrucional": True,
                "dominio": dominio,
                "operacao": "CONCLUIR",
                "resposta": resposta
            }

        if re.search(
            r"\b(?:cancelar|cancelo|cancela)\b",
            texto
        ):

            if dominio == "TAREFA":
                resposta = (
                    "Para cancelar uma tarefa na A.R.A., "
                    'diga "cancele a tarefa" seguido do nome dela.'
                )
            else:
                resposta = (
                    "Para cancelar um lembrete na A.R.A., "
                    'diga "cancele o lembrete" seguido do nome dele.'
                )

            return {
                "instrucional": True,
                "dominio": dominio,
                "operacao": "CANCELAR",
                "resposta": resposta
            }

        if (
            dominio == "TAREFA"
            and re.search(
                r"\b(?:iniciar|inicio|inicia)\b",
                texto
            )
        ):
            return {
                "instrucional": True,
                "dominio": "TAREFA",
                "operacao": "INICIAR",
                "resposta": (
                    "Para iniciar uma tarefa na A.R.A., "
                    'diga "inicie a tarefa" seguido do nome dela.'
                )
            }

        if (
            dominio == "TAREFA"
            and re.search(
                r"\b(?:reabrir|reabro|reabra)\b",
                texto
            )
        ):
            return {
                "instrucional": True,
                "dominio": "TAREFA",
                "operacao": "REABRIR",
                "resposta": (
                    "Para reabrir uma tarefa na A.R.A., "
                    'diga "reabra a tarefa" seguido do nome dela.'
                )
            }

        if re.search(
            r"\b(?:editar|edito|edita|alterar|altero|mudar|mudo)\b",
            texto
        ):

            if dominio == "TAREFA":
                resposta = (
                    "Você pode pedir diretamente a alteração da tarefa, "
                    "informando qual tarefa deseja modificar e o novo valor."
                )
            else:
                resposta = (
                    "Você pode pedir diretamente a alteração do lembrete, "
                    "informando qual lembrete deseja modificar e o novo valor."
                )

            return {
                "instrucional": True,
                "dominio": dominio,
                "operacao": "EDITAR",
                "resposta": resposta
            }

        # Há formato instrucional + domínio, mas não uma operação
        # operacional conhecida com segurança.
        return None
