from app.ai.groq_provider import GroqProvider


class AIEngine:

    def __init__(self):
        self.provider = GroqProvider()

    def gerar_resposta(
        self,
        mensagens,
        temperatura=0.7
    ):
        return self.provider.gerar_resposta(
            mensagens=mensagens,
            temperatura=temperatura
        )


ai_engine = AIEngine()
