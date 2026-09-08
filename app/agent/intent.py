from dataclasses import dataclass, field
from enum import Enum

from pydantic import fields


class TipoAcao(str, Enum):
    CONVERSAR = "CONVERSAR"
    EXECUTAR = "EXECUTAR"




@dataclass
class AgentDecision:
    acao: TipoAcao
    ferramenta: str | None = None
    argumentos: dict = field(default_factory=dict)