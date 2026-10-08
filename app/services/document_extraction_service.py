from __future__ import annotations

from pathlib import Path

from sqlalchemy.orm import Session

from app.integrations.document.docx_extractor import (
    DocxExtractor
)
from app.integrations.document.pdf_extractor import (
    PdfExtractor
)
from app.integrations.document.txt_extractor import (
    TxtExtractor
)

from app.models.arquivo import (
    Arquivo
)

from app.repositories.arquivo_repository import (
    ArquivoRepository
)


class DocumentExtractionService:

    _extractors = {
        "txt":
            TxtExtractor(),

        "docx":
            DocxExtractor(),

        "pdf":
            PdfExtractor()
    }


    @classmethod
    def extrair(
        cls,
        db: Session,
        arquivo: Arquivo
    ) -> Arquivo:

        extensao = (
            str(
                arquivo.extensao
                or ""
            )
            .lower()
            .lstrip(".")
        )


        extractor = (
            cls._extractors.get(
                extensao
            )
        )


        if extractor is None:

            raise ValueError(
                "Não existe extrator para "
                f"arquivos {extensao.upper()}."
            )


        caminho = Path(
            arquivo.caminho
        )


        if not caminho.exists():

            raise FileNotFoundError(
                "O arquivo físico não foi encontrado."
            )


        ArquivoRepository.atualizar_status(
            db=db,
            arquivo=arquivo,
            status="PROCESSANDO"
        )


        try:

            texto = (
                extractor.extrair(
                    caminho
                )
            )


            texto = (
                texto.strip()
            )


            if not texto:

                raise ValueError(
                    "Nenhum texto foi encontrado "
                    "no documento."
                )


            return (
                ArquivoRepository
                .salvar_texto_extraido(
                    db=db,
                    arquivo=arquivo,
                    texto_extraido=texto
                )
            )


        except Exception as erro:

            ArquivoRepository.atualizar_status(
                db=db,
                arquivo=arquivo,
                status="ERRO",
                erro_processamento=str(
                    erro
                )
            )

            raise