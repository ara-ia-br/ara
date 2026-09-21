from dataclasses import dataclass, field
from enum import Enum


class TipoAcao(str, Enum):
    CONVERSAR = "CONVERSAR"
    EXECUTAR = "EXECUTAR"




@dataclass
class AgentDecision:
    acao: TipoAcao
    ferramenta: str | None = None
    argumentos: dict = field(default_factory=dict)
    
    

@dataclass
class AgentPlanStep:
    decisao: AgentDecision
    
    
    '''
    Índice da etapa anterior da qual esta ação depende.
    None significa que a etapa pode ser executada diretamente.
    '''
    depende_de: int | None = None
    
    
    '''
    Argumentos que serão preenchidos usando o resultado de uma etapa anterior.
    
    Ex:
    
        {
            "id_tarefa": {
                "resultado_de": 0,
                "campo": "id_tarefa"
            },
            "data_hora": {
                "resultado_de": 0,
                "campo": "data_limite",
                "offset_minutos": -30
                }
        }
    '''
    
    resolver_argumentos: dict = field(default_factory=dict)
    


@dataclass
class AgentPlan:
    passos: list[AgentPlanStep] = field(default_factory=list)
    
    