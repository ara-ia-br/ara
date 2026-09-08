from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class MemoriaCreate(BaseModel):
    id_usuario: int

    tipo_memoria: str = Field(
        min_length=1,
        max_length=50
    )

    conteudo: str = Field(
        min_length=1
    )

    importancia: Decimal = Field(
        default=Decimal("0.00"),
        ge=0,
        le=100
    )

    data_expiracao: datetime | None = None


class MemoriaResponse(BaseModel):
    id_memoria: int
    id_usuario: int
    tipo_memoria: str
    conteudo: str
    importancia: Decimal

    data_criacao: datetime | None
    data_atualizacao: datetime | None
    data_expiracao: datetime | None

    ativa: bool

    model_config = ConfigDict(
        from_attributes=True
    )