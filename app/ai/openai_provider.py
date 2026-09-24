from openai import OpenAI

from app.ai.base import AIProvider
from app.security.settings import setting


class OpenAIProvider(AIProvider):

    def __init__(self):

        self.client = OpenAI(
            api_key=setting.OPENAI_API_KEY,
            timeout=60.0,
            max_retries=2
        )

        self.modelo = setting.OPENAI_MODEL

    def gerar_resposta(
        self,
        mensagens: list[dict],
        temperatura: float = 0.5,
        max_tokens: int | None = None
    ) -> str:

        if not mensagens:
            raise ValueError(
                "Nenhuma mensagem foi enviada para a IA."
            )

        entrada = []

        for mensagem in mensagens:

            role = mensagem.get(
                "role",
                "user"
            )

            conteudo = mensagem.get(
                "content",
                ""
            )

            if not conteudo:
                continue

            if role not in {
                "system",
                "developer",
                "user",
                "assistant"
            }:
                role = "user"

            entrada.append(
                {
                    "role": role,
                    "content": str(conteudo)
                }
            )

        if not entrada:
            raise ValueError(
                "Nenhuma mensagem válida foi enviada."
            )

        limite_tokens = (
            max_tokens
            if max_tokens is not None
            else 1500
        )

        resposta = (
            self.client.responses.create(
                model=self.modelo,
                input=entrada,
                reasoning={
                    "effort":
                        setting.OPENAI_REASONING_EFFORT
                },
                service_tier=
                    setting.OPENAI_SERVICE_TIER,
                max_output_tokens=limite_tokens,
                store=False
            )
        )

        texto = (
            resposta.output_text
            or ""
        ).strip()

        if not texto:
            raise RuntimeError(
                "OpenAI não retornou texto."
            )

        return texto