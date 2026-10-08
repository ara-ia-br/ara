from __future__ import annotations

from pathlib import Path

from app.integrations.document.base import (
    DocumentExtractor
)


class TxtExtractor(DocumentExtractor):

    def extrair(
        self,
        caminho: Path
    ) -> str:

        tentativas = [
            "utf-8",
            "utf-8-sig",
            "latin-1"
        ]

        for encoding in tentativas:

            try:

                return caminho.read_text(
                    encoding=encoding
                )

            except UnicodeDecodeError:
                continue


        raise ValueError(
            "Não foi possível interpretar "
            "o conteúdo do arquivo TXT."
        )