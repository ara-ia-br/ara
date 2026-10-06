from typing import Any

from pydantic import BaseModel, Field


class LocalizacaoRequest(BaseModel):
    latitude: float = Field(
        ge=-90,
        le=90
    )

    longitude: float = Field(
        ge=-180,
        le=180
    )

    accuracy: float | None = Field(
        default=None,
        ge=0
    )

    timestamp: float | None = None


class RecalcularRotaRequest(BaseModel):
    destino: str = Field(
        min_length=1
    )

    latitude: float = Field(
        ge=-90,
        le=90
    )

    longitude: float = Field(
        ge=-180,
        le=180
    )


class RecalcularRotaResponse(BaseModel):
    resposta_ara: str

    visualizacao: (
        dict[str, Any]
        | None
    ) = None


class ChatRequest(BaseModel):
    id_conversa: int

    mensagem: str = Field(
        min_length=1
    )

    localizacao: (
        LocalizacaoRequest
        | None
    ) = None


class ChatResponse(BaseModel):
    id_conversa: int
    mensagem_usuario: str
    resposta_ara: str
    modelo: str

    ferramenta: (
        str
        | None
    ) = None

    tempo_processamento: float

    visualizacao: (
        dict[str, Any]
        | None
    ) = None