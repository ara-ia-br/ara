from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UsuarioCreate(BaseModel):
    nome: str = Field(min_length=2, max_length=100)
    email: EmailStr
    senha: str = Field(min_length=8, max_length=100)



class UsuarioResponse(BaseModel) :
    id_usuario: int
    nome: str
    email: EmailStr
    data_cadastro: datetime
    data_ultimo_acesso: datetime | None
    ativo: bool

    model_config = ConfigDict(from_attributes=True)