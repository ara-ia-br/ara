from __future__ import annotations

from pathlib import Path

from pypdf import PdfReader

from app.integrations.document.base import (
    DocumentExtractor
)


class PdfExtractor(DocumentExtractor):

    def extrair(
        self,
        caminho: Path
    ) -> str:

        reader = PdfReader(
            str(caminho)
        )

        paginas: list[str] = []


        for numero, pagina in enumerate(
            reader.pages,
            start=1
        ):

            texto = (
                pagina.extract_text()
                or ""
            ).strip()

            if not texto:
                continue


            paginas.append(
                (
                    f"[Página {numero}]\n"
                    f"{texto}"
                )
            )


        texto_final = (
            "\n\n".join(
                paginas
            )
            .strip()
        )


        if not texto_final:

            raise ValueError(
                "O arquivo PDF não possui "
                "texto extraível."
            )


        return texto_final