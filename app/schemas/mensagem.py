from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import (
    BaseModel,
    ConfigDict,
    Field
)

from app.models.mensagem import (
    RemetenteMensagem
)


class MensagemCreate(BaseModel):

    id_conversa: int

    remetente: RemetenteMensagem

    conteudo: str = Field(
        min_length=1
    )

    tipo: str = Field(
        min_length=1,
        max_length=30
    )

    dados_visuais: dict[str, Any] | None = None


class MensagemResponse(BaseModel):

    id_mensagem: int

    id_conversa: int

    remetente: RemetenteMensagem

    conteudo: str

    tipo: str

    data_envio: datetime | None

    modelo_ia: str | None

    tempo_processamento: Decimal | None

    # No banco/modelo:
    # dados_visuais
    #
    # Para o frontend:
    # visualizacao
    visualizacao: dict[str, Any] | None = Field(
        default=None,
        validation_alias="dados_visuais"
    )

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )