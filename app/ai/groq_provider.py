from groq import (
    Groq,
    RateLimitError,
    APIError
)

from app.ai.base import AIProvider
from app.security.settings import setting


class GroqProvider(AIProvider):

    def __init__(self):

        self.client = Groq(
            api_key=setting.GROQ_API_KEY,
            max_retries=0,
            timeout=45.0
        )

        self.modelo = setting.GROQ_MODEL

    def gerar_resposta(
        self,
        mensagens: list[dict],
        temperatura: float = 0.7,
        max_tokens: int | None = None
    ) -> str:

        if not mensagens:
            raise ValueError(
                "Nenhuma mensagem foi enviada para a IA."
            )

        limite_tokens = (
            max_tokens
            if max_tokens is not None
            else 700
        )

        try:

            resposta = (
                self.client
                .chat
                .completions
                .create(
                    model=self.modelo,
                    messages=mensagens,
                    temperature=temperatura,
                    max_completion_tokens=limite_tokens
                )
            )

        except RateLimitError as erro:

            raise RuntimeError(
                "Groq atingiu o limite de requisições."
            ) from erro

        except APIError as erro:

            raise RuntimeError(
                "Erro na API Groq."
            ) from erro

        conteudo = (
            resposta
            .choices[0]
            .message
            .content
            or ""
        ).strip()

        if not conteudo:
            raise RuntimeError(
                "Groq não retornou conteúdo."
            )

        return conteudo