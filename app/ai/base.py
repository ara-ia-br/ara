from abc import ABC, abstractmethod

class AIProvider(ABC):
    @abstractmethod
    def gerar_resposta(
            self,
            mensagens: list[dict],
            temperatura: float = 0.5,
            max_tokens: int | None = None
    ) -> str:
        """
        Gera uma resposta a partir do histórico fornecido.
        """
        raise NotImplementedError
