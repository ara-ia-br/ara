from dataclasses import dataclass

import re


@dataclass
class IntentSegment:
    texto: str
    referencia_anterior: bool = False


class MultiIntentParser:

    @staticmethod
    def dividir(
        mensagem: str
    ) -> list[IntentSegment]:

        texto = mensagem.strip()

        if not texto:
            return []

        # =====================================================
        # TAREFA + LEMBRETE RELATIVO
        # =====================================================
        #
        # Ex:
        # crie uma tarefa chamada estudar amanhã às 19h
        # e me lembre dela 30 minutos antes
        # =====================================================

        match = re.search(
            r"^(?P<primeira>.+?)"
            r"\s+e\s+"
            r"(?P<segunda>"
            r"(?:me\s+)?"
            r"(?:lembre|lembra)"
            r".+"
            r")$",
            texto,
            flags=re.IGNORECASE
        )

        if match:

            primeira = (
                match.group("primeira")
                .strip()
            )

            segunda = (
                match.group("segunda")
                .strip()
            )

            referencia_anterior = bool(
                re.search(
                    r"\b("
                    r"dela|dele|"
                    r"ela|ele|"
                    r"dessa\s+tarefa|"
                    r"desta\s+tarefa|"
                    r"essa\s+tarefa|"
                    r"esta\s+tarefa"
                    r")\b",
                    segunda,
                    flags=re.IGNORECASE
                )
            )

            return [
                IntentSegment(
                    texto=primeira,
                    referencia_anterior=False
                ),
                IntentSegment(
                    texto=segunda,
                    referencia_anterior=
                        referencia_anterior
                )
            ]

        # =====================================================
        # MENSAGEM SIMPLES
        # =====================================================

        return [
            IntentSegment(
                texto=texto,
                referencia_anterior=False
            )
        ]