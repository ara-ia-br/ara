from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field, ConfigDict

from app.models.mensagem import RemetenteMensagem


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

class MensagemResponse(BaseModel):
    id_mensagem: int
    id_conversa: int
    remetente: RemetenteMensagem
    conteudo: str
    tipo: str

    data_envio: datetime | None
    modelo_ia: str | None

    tempo_processamento: Decimal | None

    model_config = ConfigDict(from_attributes=True)