from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    id_conversa: int
    mensagem: str = Field(min_length=1)


class ChatResponse(BaseModel):
    id_conversa: int
    mensagem_usuario: str
    resposta_ara: str
    modelo: str
    ferramenta: str | None = None
    tempo_processamento: float