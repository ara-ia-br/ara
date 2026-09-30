import re


class TitleCleanerService:

    @staticmethod
    def limpar(
        texto: str
    ) -> str:

        texto = re.sub(
            r"\bprioridade\s+(máxima|maxima|alta|baixa|muito baixa|[1-5])\b",
            "",
            texto,
            flags=re.IGNORECASE
        )

        texto = re.sub(
            r"\b(urgente|urgentemente|muito urgente)\b",
            "",
            texto,
            flags=re.IGNORECASE
        )

        texto = re.sub(
            r"\s+",
            " ",
            texto
        )

        texto = texto.strip(
            " ,.-"
        )

        texto = re.sub(
            r"^para\s+",
            "",
            texto,
            flags=re.IGNORECASE
        )

        if not texto:
            return texto

        texto = texto.strip()

        texto = re.sub(
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
            texto,
            flags=(
                re.IGNORECASE
                | re.VERBOSE
            )
        )

        texto = texto.strip(
            " ,.!?;:-"
        )

        return texto