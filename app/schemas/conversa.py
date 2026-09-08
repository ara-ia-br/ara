from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict

from app.models.conversa import Conversa, StatusConversa


class ConversaCreate(BaseModel):
    id_usuario: int
    titulo: str = Field(
        min_length=1,
        max_length=200
    )



class ConversaResponse(BaseModel):
    id_conversa: int
    id_usuario: int
    titulo: str
    data_criacao: datetime | None
    data_atualizacao: datetime | None
    status: StatusConversa

    model_config = ConfigDict(
        from_attributes=True
    )

class ConversaUpdateTitulo(BaseModel):
    titulo: str = Field(
        min_length=1,
        max_length=200
    )