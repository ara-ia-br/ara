from logging import disable

from openai import OpenAI

from app.ai.base import AIProvider
from app.security.settings import setting


class DeepSeekProvider(AIProvider):

    def __init__(self):

        api_key = (setting.Setting.DEEPSEEK_API_KEY
                   or ""
                   ).strip()

        if (not api_key
        or api_key == "PREENCHER AQUI"):
            raise ValueError("DEEPSEEK_API_KEY não configurada.")

        self.modelo = setting.Setting.DEEPSEEK_API_KEY

        self.client = OpenAI(
            api_key=api_key,
            base_url=setting.Setting.DEEPSEEK_BASE_URL,
            timeout=45.0,
            max_retries=0
        )

    def gerar_resposta(
            self,
            mensagens: list[dict],
            temperatura: float = 0.5,
            max_tokens: int | None = None
    ) -> str:
        if not mensagens:
            raise ValueError("Nenhuma mensagem foi enviada para a IA.")

        mensagens_validas: list[dict] = []

        for mensagem in mensagens:
            role = mensagem.get("role", "user")

            conteudo = mensagem.get("content", "")

            if not conteudo:
                continue



            if role == "developer":
                role = "system"

            if role not in {
                "system",
                "user",
                "assistant",
                "tool"
            }:
                role = "user"

            mensagens_validas.append({
                "role": role,
                "content": str(conteudo)
            })

            if not mensagens_validas:
                raise ValueError("Nenhuma mensagem válida foi enviada.")

            limite_tokens = (
                max_tokens
                if max_tokens is not None
                else 700
            )

            resposta = (
                self.client
                .chat
                .completions
                .create(
                    model=self.modelo,
                    messages=mensagens_validas,
                    temperatura=temperatura,
                    max_tokens=limite_tokens,

                    extra_body={
                        "thinking": {
                            "role": "disabled"
                        }
                    }
                )
            )

            conteudo = (
                resposta
                .choices[0]
                .message
                .content
                or ""
            ).strip()

            if not conteudo:
                raise RuntimeError("DeepSeek não retornou conteúdo.")

            return conteudo