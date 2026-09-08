from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.tarefa import StatusTarefa


class TarefaCreate(BaseModel):
    id_usuario: int

    titulo: str = Field(
        min_length=1,
        max_length=200
    )

    descricao: str | None = None

    prioridade: int = Field(
        default=3,
        ge=1,
        le=5
    )

    data_limite: datetime | None = None


class TarefaUpdate(BaseModel):
    titulo: str | None = Field(
        default=None,
        min_length=1,
        max_length=200
    )

    descricao: str | None = None

    prioridade: int | None = Field(
        default=None,
        ge=1,
        le=5
    )

    data_limite: datetime | None = None


class TarefaResponse(BaseModel):
    id_tarefa: int
    id_usuario: int

    titulo: str
    descricao: str | None

    prioridade: int
    status: StatusTarefa

    data_criacao: datetime | None
    data_inicio: datetime | None
    data_conclusao: datetime | None
    data_limite: datetime | None

    model_config = ConfigDict(
        from_attributes=True
    )