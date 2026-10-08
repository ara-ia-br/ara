from datetime import datetime

from pydantic import ConfigDict, BaseModel


class ArquivoUploadResponse(BaseModel):

    id_arquivo: int

    id_usuario: int

    id_conversa: int | None = None

    nome_original: str

    mime_type: str | None = None

    extensao: str

    tamanho_bytes: int

    status: str

    criado_em: datetime

    model_config = ConfigDict(
        from_attributes=True
    )