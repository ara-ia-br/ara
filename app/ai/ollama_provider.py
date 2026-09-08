from ollama import Client

from app.ai.base import AIProvider


class OllamaProvider(AIProvider):

    def __init__(
        self,
        modelo: str = "qwen3.5:4b"
    ):
        self.modelo = modelo

        self.client = Client(
            host="http://localhost:11434"
        )


    def gerar_resposta(
        self,
        mensagens: list[dict]
    ) -> str:

        resposta = self.client.chat(
            model=self.modelo,
            messages=mensagens,

            # Mantém o modelo carregado na memória
            # para as próximas requisições.
            keep_alive="30m",

            # Evita raciocínio extra quando não for necessário.
            # Para Qwen isso ajuda bastante na latência.
            think=False,

            options={
                # Limita o contexto inicialmente.
                # Depois podemos aumentar se precisar.
                "num_ctx": 8192,

                # Limita tamanho máximo da resposta.
                "num_predict": 800,

                # Respostas naturais, sem muita aleatoriedade.
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