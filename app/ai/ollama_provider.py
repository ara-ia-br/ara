from ollama import Client

from app.ai.base import AIProvider
from app.security.settings import setting


class OllamaProvider(AIProvider):

    def __init__(
        self,
        modelo: str | None = None,
        base_url: str | None = None
    ):
        self.modelo = modelo or setting.OLLAMA_MODEL
        self.base_url = base_url or setting.OLLAMA_BASE_URL

        self.client = Client(
            host=self.base_url
        )

    def gerar_resposta(
        self,
        mensagens: list[dict]
    ) -> str:

        resposta = self.client.chat(
            model=self.modelo,
            messages=mensagens,
            keep_alive="30m",
            think=False,
            options={
                "num_ctx": 8192,
                "num_predict": 800,
                "temperature": 0.5
            }
        )

        conteudo = (
            resposta.message.content
            or ""
        ).strip()

        if not conteudo:
            raise RuntimeError(
                "O modelo não retornou conteúdo."
            )

        return conteudo