from app.ai.base import AIProvider

from app.ai.ollama_provider import (
    OllamaProvider
)


class AIEngine:

    def __init__(
        self,
        provider: AIProvider | None = None
    ):

        self.provider = (
            provider
            if provider is not None
            else OllamaProvider()
        )


    def gerar_resposta(
        self,
        mensagens: list[dict]
    ) -> str:

        return self.provider.gerar_resposta(
            mensagens
        )


ai_engine = AIEngine()