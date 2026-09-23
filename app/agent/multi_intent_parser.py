from dataclasses import dataclass

import re


@dataclass
class IntentSegment:
    texto: str
    referencia_anterior: bool = False


class MultiIntentParser:

    # =========================================================
    # INÍCIOS EXPLÍCITOS DE UMA NOVA INTENÇÃO
    # =========================================================

    _INICIOS_INTENT = (
        r"(?:"
        r"me\s+lembre|me\s+lembra|"
        r"lembre|lembra|"
        r"liste|lista|listar|"
        r"mostre|mostra|"
        r"crie|cria|criar|"
        r"adicione|adiciona|adicionar|"
        r"edite|edita|editar|"
        r"altere|altera|alterar|"
        r"mude|muda|"
        r"inicie|inicia|"
        r"conclua|conclui|"
        r"cancele|cancela|"
        r"reabra|reabre|"
        r"renomeie|renomeia|"
        r"exclua|exclui"
        r")\b"
    )

    # =========================================================
    # REFERÊNCIA AO RESULTADO / ENTIDADE ANTERIOR
    # =========================================================

    @staticmethod
    def _tem_referencia_anterior(
        texto: str
    ) -> bool:

        return bool(
            re.search(
                r"\b(?:"
                r"dela|dele|"
                r"ela|ele|"
                r"dessa\s+tarefa|"
                r"desta\s+tarefa|"
                r"essa\s+tarefa|"
                r"esta\s+tarefa|"
                r"desse\s+lembrete|"
                r"deste\s+lembrete|"
                r"esse\s+lembrete|"
                r"este\s+lembrete"
                r")\b",
                texto,
                flags=re.IGNORECASE
            )
        )

    # =========================================================
    # LISTAGEM COM VERBO COMPARTILHADO
    # =========================================================
    #
    # Exemplos:
    #
    # "liste minhas tarefas e meus lembretes"
    # "lista minhas tarefas e lembretes"
    # "lista minhas tarefa e meus lembretes"
    #
    # Linguisticamente existe apenas um verbo explícito,
    # mas existem duas operações independentes.
    # =========================================================

    @staticmethod
    def _dividir_listagem_compartilhada(
        texto: str
    ) -> list[IntentSegment] | None:

        # -----------------------------------------------------
        # TAREFAS -> LEMBRETES
        # -----------------------------------------------------

        match = re.fullmatch(
            r"(?:"
            r"liste|lista|listar|"
            r"mostre|mostra"
            r")\s+"
            r"(?:(?:minha|minhas)\s+)?"
            r"tarefas?"
            r"\s+e\s+"
            r"(?:(?:meu|meus|minha|minhas)\s+)?"
            r"lembretes?"
            r"\s*[.!?]*",
            texto,
            flags=re.IGNORECASE
        )

        if match:

            return [
                IntentSegment(
                    texto="liste minhas tarefas",
                    referencia_anterior=False
                ),
                IntentSegment(
                    texto="liste meus lembretes",
                    referencia_anterior=False
                )
            ]

        # -----------------------------------------------------
        # LEMBRETES -> TAREFAS
        # -----------------------------------------------------

        match = re.fullmatch(
            r"(?:"
            r"liste|lista|listar|"
            r"mostre|mostra"
            r")\s+"
            r"(?:(?:meu|meus|minha|minhas)\s+)?"
            r"lembretes?"
            r"\s+e\s+"
            r"(?:(?:minha|minhas)\s+)?"
            r"tarefas?"
            r"\s*[.!?]*",
            texto,
            flags=re.IGNORECASE
        )

        if match:

            return [
                IntentSegment(
                    texto="liste meus lembretes",
                    referencia_anterior=False
                ),
                IntentSegment(
                    texto="liste minhas tarefas",
                    referencia_anterior=False
                )
            ]

        return None

    # =========================================================
    # DIVIDIR
    # =========================================================

    @staticmethod
    def dividir(
        mensagem: str
    ) -> list[IntentSegment]:

        texto = mensagem.strip()

        if not texto:
            return []

        # =====================================================
        # 1. ELIPSE / VERBO COMPARTILHADO
        # =====================================================

        segmentos_compartilhados = (
            MultiIntentParser
            ._dividir_listagem_compartilhada(
                texto
            )
        )

        if segmentos_compartilhados is not None:
            return segmentos_compartilhados

        # =====================================================
        # 2. INTENÇÕES COM VERBOS EXPLÍCITOS
        # =====================================================

        partes = re.split(
            rf"\s+e\s+(?="
            rf"{MultiIntentParser._INICIOS_INTENT}"
            rf")",
            texto,
            flags=re.IGNORECASE
        )

        segmentos: list[IntentSegment] = []

        for indice, parte in enumerate(partes):

            parte = parte.strip()

            if not parte:
                continue

            segmentos.append(
                IntentSegment(
                    texto=parte,
                    referencia_anterior=(
                        indice > 0
                        and MultiIntentParser
                        ._tem_referencia_anterior(
                            parte
                        )
                    )
                )
            )

        return segmentos