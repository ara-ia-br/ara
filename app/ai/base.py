from abc import ABC, abstractmethod

class AIProvider(ABC):
    @abstractmethod
    def gerar_resposta(self, mensagems: list[dict]) -> str:
        pass
