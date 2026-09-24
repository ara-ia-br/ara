from app.ai.model_router import ModelRouter


class AIEngine:

    def __init__(self):

        self.router = ModelRouter()

    def gerar_resposta(
        self,
        mensagens: list[dict],
        temperatura: float = 0.5,
        max_tokens: int | None = None
    ) -> str:

        try:

            return self.router.gerar_resposta(
                mensagens=mensagens,
                temperatura=temperatura,
                max_tokens=max_tokens
            )

        except Exception as erro:

            print(
                "[AI ENGINE] "
                f"{type(erro).__name__}: {erro}"
            )

            return (
                "O serviço de inteligência está "
                "temporariamente indisponível. "
                "Tente novamente em instantes."
            )


ai_engine = AIEngine()