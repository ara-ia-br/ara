from __future__ import annotations

import mimetypes
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.arquivo import Arquivo
from app.models.conversa import Conversa
from app.repositories.arquivo_repository import (
    ArquivoRepository
)


class FileService:

    STORAGE_ROOT = Path(
        "storage/uploads"
    )

    EXTENSOES_PERMITIDAS = {
        ".pdf",
        ".docx",
        ".txt"
    }

    TAMANHO_MAXIMO_BYTES = (
        20 * 1024 * 1024
    )

    CHUNK_SIZE = (
        1024 * 1024
    )


    # =========================================================
    # VALIDAR CONVERSA
    # =========================================================

    @staticmethod
    def _validar_conversa(
        db: Session,
        id_usuario: int,
        id_conversa: int | None
    ) -> None:

        if id_conversa is None:
            return

        conversa = (
            db.execute(
                select(
                    Conversa
                )
                .where(
                    Conversa.id_conversa
                    == id_conversa,
                    Conversa.id_usuario
                    == id_usuario
                )
            )
            .scalar_one_or_none()
        )

        if conversa is None:

            raise ValueError(
                "A conversa informada não existe "
                "ou não pertence ao usuário."
            )


    # =========================================================
    # NOME ORIGINAL
    # =========================================================

    @staticmethod
    def _obter_nome_original(
        upload: UploadFile
    ) -> str:

        nome = Path(
            upload.filename or ""
        ).name.strip()

        if not nome:

            raise ValueError(
                "O arquivo não possui um nome válido."
            )

        return nome


    # =========================================================
    # EXTENSÃO
    # =========================================================

    @classmethod
    def _obter_extensao(
        cls,
        nome_original: str
    ) -> str:

        extensao = (
            Path(
                nome_original
            )
            .suffix
            .lower()
        )

        if (
            extensao
            not in cls.EXTENSOES_PERMITIDAS
        ):

            raise ValueError(
                "Formato de arquivo não suportado. "
                "Use PDF, DOCX ou TXT."
            )

        return extensao


    # =========================================================
    # UPLOAD
    # =========================================================

    @classmethod
    async def salvar_upload(
        cls,
        db: Session,
        id_usuario: int,
        upload: UploadFile,
        id_conversa: int | None = None
    ) -> Arquivo:

        cls._validar_conversa(
            db=db,
            id_usuario=id_usuario,
            id_conversa=id_conversa
        )


        nome_original = (
            cls._obter_nome_original(
                upload
            )
        )


        extensao = (
            cls._obter_extensao(
                nome_original
            )
        )


        # =====================================================
        # PASTA DO USUÁRIO
        # =====================================================

        pasta_usuario = (
            cls.STORAGE_ROOT
            / str(id_usuario)
        )

        pasta_usuario.mkdir(
            parents=True,
            exist_ok=True
        )


        # =====================================================
        # NOME INTERNO SEGURO
        # =====================================================

        nome_armazenado = (
            f"{uuid4().hex}"
            f"{extensao}"
        )


        caminho_arquivo = (
            pasta_usuario
            / nome_armazenado
        )


        tamanho_bytes = 0


        try:

            # =================================================
            # GRAVAÇÃO EM CHUNKS
            # =================================================

            with caminho_arquivo.open(
                "wb"
            ) as destino:

                while True:

                    chunk = await upload.read(
                        cls.CHUNK_SIZE
                    )

                    if not chunk:
                        break


                    tamanho_bytes += len(
                        chunk
                    )


                    if (
                        tamanho_bytes
                        > cls.TAMANHO_MAXIMO_BYTES
                    ):

                        raise ValueError(
                            "O arquivo excede o limite "
                            "de 20 MB."
                        )


                    destino.write(
                        chunk
                    )


            if tamanho_bytes <= 0:

                raise ValueError(
                    "O arquivo enviado está vazio."
                )


            # =================================================
            # MIME TYPE
            # =================================================

            mime_type = (
                upload.content_type
                or mimetypes.guess_type(
                    nome_original
                )[0]
            )


            # =================================================
            # BANCO
            # =================================================

            arquivo = Arquivo(

                id_usuario=
                    id_usuario,

                id_conversa=
                    id_conversa,

                nome_original=
                    nome_original,

                nome_armazenado=
                    nome_armazenado,

                mime_type=
                    mime_type,

                extensao=
                    extensao.lstrip("."),

                tamanho_bytes=
                    tamanho_bytes,

                caminho=
                    caminho_arquivo
                    .as_posix(),

                status=
                    "ENVIADO"
            )


            return (
                ArquivoRepository.criar(
                    db=db,
                    arquivo=arquivo
                )
            )


        except Exception:

            db.rollback()

            if caminho_arquivo.exists():

                try:
                    caminho_arquivo.unlink()

                except OSError:
                    pass

            raise


        finally:

            await upload.close()