from groq import Groq, RateLimitError, APIError

from app.security.settings import setting


class GroqProvider:

    def __init__(self):
        self.client = Groq(
            api_key=setting.GROQ_API_KEY,

            # Evita que uma requisição simples fique
            # presa em vários retries automáticos.
            max_retries=0,

            timeout=45.0
        )

    def gerar_resposta(
        self,
        mensagens,
        temperatura=0.7
    ):
        try:
            resposta = self.client.chat.completions.create(
                model=setting.GROQ_MODEL,
                messages=mensagens,
                temperature=temperatura,

                # Impede respostas desnecessariamente enormes.
                max_completion_tokens=700
            )

            conteudo = (
                resposta
                .choices[0]
                .message
                .content
            )

            if not conteudo:
                return (
                    "Não consegui gerar uma resposta agora. "
                    "Tente novamente."
                )

            return conteudo

        except RateLimitError:
            return (
                "Estou recebendo muitas solicitações neste "
                "momento. Aguarde alguns segundos e tente "
                "novamente."
            )

        except APIError as erro:
            print(
                "[GROQ API ERROR]",
                type(erro).__name__,
                str(erro)
            )

            return (
                "O serviço de inteligência está "
                "temporariamente indisponível. "
                "Tente novamente em instantes."
            )
