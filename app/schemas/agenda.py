from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class LembreteCreate(BaseModel):
    id_usuario: int
    titulo: str = Field(min_length=1, max_length=200)
    descricao: str | None = Field(default=None, max_length=5000)
    data_hora: datetime
    recorrencia: str | None = Field(default=None, max_length=100)


class LembreteUpdate(BaseModel):
    titulo: str | None = Field(default=None, min_length=1, max_length=200)
    descricao: str | None = Field(default=None, max_length=5000)
    data_hora: datetime | None = None
    recorrencia: str | None = Field(default=None, max_length=100)
    status: str | None = Field(default=None, max_length=20)


class LembreteResponse(BaseModel):
    id_lembrete: int
    id_usuario: int
    id_tarefa: int | None
    titulo: str
    descricao: str | None
    data_hora: datetime
    recorrencia: str | None
    status: str
    data_criacao: datetime | None

    model_config = ConfigDict(from_attributes=True)
