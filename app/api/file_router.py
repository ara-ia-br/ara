from __future__ import annotations

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    status
)

from sqlalchemy.orm import Session

from app.repositories.arquivo_repository import (
    ArquivoRepository
)

from app.services.document_extraction_service import (
    DocumentExtractionService
)

from app.schemas.file import (ArquivoUploadResponse)

from app.database.connection import (
    get_db
)


from app.security.depedencies import (
    obter_usuario_atual
)

from app.services.file_service import (
    FileService
)


router = APIRouter(
    prefix="/arquivos",
    tags=["Arquivos"]
)


# =========================================================
# UPLOAD
# =========================================================

@router.post(
    "/upload",
    response_model=ArquivoUploadResponse,
    status_code=status.HTTP_201_CREATED
)
async def upload_arquivo(

    arquivo: UploadFile = File(...),

    id_conversa: int | None = Form(
        default=None
    ),

    db: Session = Depends(
        get_db
    ),

    usuario_atual=Depends(
        obter_usuario_atual
    )
):

    try:

        return await FileService.salvar_upload(

            db=db,

            id_usuario=
                usuario_atual.id_usuario,

            upload=
                arquivo,

            id_conversa=
                id_conversa
        )


    except ValueError as erro:

        raise HTTPException(
            status_code=
                status.HTTP_400_BAD_REQUEST,

            detail=
                str(erro)
        ) from erro


    except Exception as erro:

        print(
            "[FILE UPLOAD] Erro:",
            repr(erro)
        )

        raise HTTPException(
            status_code=
                status.HTTP_500_INTERNAL_SERVER_ERROR,

            detail=(
                "Não foi possível enviar "
                "o arquivo."
            )
        ) from erro


@router.post(
    "/{id_arquivo}/processar",
    response_model=ArquivoUploadResponse
)
def processar_arquivo(
    id_arquivo: int,

    db: Session = Depends(
        get_db
    ),

    usuario_atual=Depends(
        obter_usuario_atual
    )
):

    arquivo = (
        ArquivoRepository.buscar_por_id(
            db=db,
            id_arquivo=id_arquivo
        )
    )


    if (
        arquivo is None
        or arquivo.id_usuario
        != usuario_atual.id_usuario
    ):

        raise HTTPException(
            status_code=404,
            detail="Arquivo não encontrado."
        )


    try:

        return (
            DocumentExtractionService
            .extrair(
                db=db,
                arquivo=arquivo
            )
        )


    except Exception as erro:

        print(
            "[DOCUMENT EXTRACTION] Erro:",
            repr(erro)
        )

        raise HTTPException(
            status_code=400,
            detail=str(erro)
        ) from erro