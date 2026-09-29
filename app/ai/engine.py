from app.ai.model_router import ModelRouter
from app.ai.result import AIResult


class AIEngine:

    def __init__(self):

        self.router = ModelRouter()

    # =====================================================
    # RESULTADO COMPLETO
    # =====================================================

    def gerar_resultado(
        self,
        mensagens: list[dict],
        temperatura: float = 0.5,
        max_tokens: int | None = None
    ) -> AIResult:

        try:

            return self.router.gerar_resultado(
                mensagens=mensagens,
                temperatura=temperatura,
                max_tokens=max_tokens
            )

        except Exception as erro:

            print(
                "[AI ENGINE] "
                f"{type(erro).__name__}: {erro}"
            )

            return AIResult(
                resposta=(
                    "O serviço de inteligência está "
                    "temporariamente indisponível. "
                    "Tente novamente em instantes."
                ),
                provider="system",
                modelo="AI_ENGINE"
            )

    # =====================================================
    # COMPATIBILIDADE — RETORNA SOMENTE TEXTO
    # =====================================================

    def gerar_resposta(
        self,
        mensagens: list[dict],
        temperatura: float = 0.5,
        max_tokens: int | None = None
    ) -> str:

        resultado = self.gerar_resultado(
            mensagens=mensagens,
            temperatura=temperatura,
            max_tokens=max_tokens
        )

        return resultado.resposta


ai_engine = AIEngine()