from dataclasses import dataclass


@dataclass(frozen=True)
class AIResult:
    resposta: str
    provider: str
    modelo: str

