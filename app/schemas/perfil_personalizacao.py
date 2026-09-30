from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict


class PerfilPersonalizacaoCreate(BaseModel):

    tom: str = Field(
        default="ADAPTATIVO",
        min_length=2,
        max_length=30
    )

    formalidade: str = Field(
        default="ADAPTATIVA",
        min_length=2,
        max_length=30
    )

    nivel_detalhe: str = Field(
        default="MEDIO",
        min_length=2,
        max_length=20
    )

    usar_emojis: bool = True

    estilo_resposta: str = Field(
        default="NATURAL",
        min_length=2,
        max_length=30
    )

    instrucoes_personais: str | None = Field(
        default=None,
        max_length=2000
    )


class PerfilPersonalizacaoUpdate(BaseModel):

    tom: str | None = Field(
        default=None,
        min_length=2,
        max_length=30
    )

    formalidade: str | None = Field(
        default=None,
        min_length=2,
        max_length=30
    )

    nivel_detalhe: str | None = Field(
        default=None,
        min_length=2,
        max_length=20
    )

    usar_emojis: bool | None = None

    estilo_resposta: str | None = Field(
        default=None,
        min_length=2,
        max_length=30
    )

    instrucoes_personais: str | None = Field(
        default=None,
        max_length=2000
    )

class PerfilPersonalizacaoResponse(BaseModel):

    id_perfil: int
    id_usuario: int

    tom: str
    formalidade: str
    nivel_detalhe: str
    usar_emojis: bool
    estilo_resposta: str

    instrucoes_personais: str | None

    data_criacao: datetime
    data_atualizacao: datetime

    model_config = ConfigDict(
        from_attributes=True
    )