from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ProjetoCreate(BaseModel):
    id_usuario: int
    nome: str = Field(min_length=1, max_length=120)
    descricao: str | None = Field(default=None, max_length=5000)


class ProjetoUpdate(BaseModel):
    nome: str | None = Field(default=None, min_length=1, max_length=120)
    descricao: str | None = Field(default=None, max_length=5000)


class ProjetoResponse(BaseModel):
    id_projeto: int
    id_usuario: int
    nome: str
    descricao: str | None
    data_criacao: datetime | None
    data_atualizacao: datetime | None

    model_config = ConfigDict(from_attributes=True)
