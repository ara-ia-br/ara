from app.ai.base import AIProvider
from app.ai.deepseek_provider import DeepSeekProvider
from app.ai.groq_provider import GroqProvider
from app.ai.openai_provider import OpenAIProvider
from app.security.settings import setting


class ModelRouter:

    _PROVIDERS = {
        "deepseek": DeepSeekProvider,
        "groq": GroqProvider,
        "openai": OpenAIProvider
    }

    def __init__(self):

        self.provider_principal = (
            setting.AI_PROVIDER
            .strip()
            .lower()
        )

        self.provider_fallback = (
            setting.AI_FALLBACK_PROVIDER
            .strip()
            .lower()
        )

        self._instancias: dict[
            str,
            AIProvider
        ] = {}

    # =====================================================
    # OBTER PROVIDER
    # =====================================================

    def _obter_provider(
        self,
        nome: str
    ) -> AIProvider:

        nome = nome.strip().lower()

        if nome in self._instancias:
            return self._instancias[nome]

        classe_provider = (
            self._PROVIDERS.get(nome)
        )

        if classe_provider is None:
            raise ValueError(
                f"Provider de IA desconhecido: {nome}"
            )

        provider = classe_provider()

        self._instancias[nome] = provider

        return provider

    # =====================================================
    # GERAR RESPOSTA
    # =====================================================

    def gerar_resposta(
        self,
        mensagens: list[dict],
        temperatura: float = 0.5,
        max_tokens: int | None = None
    ) -> str:

        providers = [
            self.provider_principal
        ]

        if (
            self.provider_fallback
            and self.provider_fallback
            != self.provider_principal
        ):
            providers.append(
                self.provider_fallback
            )

        erros: list[str] = []

        for nome_provider in providers:

            try:

                provider = self._obter_provider(
                    nome_provider
                )

                resposta = provider.gerar_resposta(
                    mensagens=mensagens,
                    temperatura=temperatura,
                    max_tokens=max_tokens
                )

                print(
                    "[MODEL ROUTER] "
                    f"provider={nome_provider}"
                )

                return resposta

            except Exception as erro:

                print(
                    "[MODEL ROUTER] "
                    f"falha provider={nome_provider} | "
                    f"{type(erro).__name__}: {erro}"
                )

                erros.append(
                    f"{nome_provider}: "
                    f"{type(erro).__name__}"
                )

        raise RuntimeError(
            "Nenhum provider de IA conseguiu "
            "processar a solicitação. "
            f"Tentativas: {', '.join(erros)}"
        )