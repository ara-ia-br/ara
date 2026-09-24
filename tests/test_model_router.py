import pytest

from app.ai.model_router import ModelRouter
from tests.test_ai import mensagens


class ProviderSucesso:

    def __init__(self):
        self.chamadas = 0


    def gerar_resposta(
            self,
            mensagens,
            temperatura=0.5,
            max_tokens=None
    ):
        self.chamadas += 1
        return "resposta-sucesso"


class ProviderFalha:
    def __int__(self):
        self.chamadas = 0

    def gerar_resposta(
            self,
            mensagens,
            temperatura=0.5,
            max_tokens=None
    ):
        self.chamadas += 1

        raise RuntimeError("Falha simulada.")


def test_provider_principal_responde():

    router = ModelRouter()

    router.provider_principal = "principal"
    router.provider_fallback = "fallback"

    router._PROVIDERS = {
        "principal": ProviderSucesso,
        "fallback": ProviderFalha
    }

    resposta = router.gerar_resposta(
        mensagens=[
            {
                "role": "user",
                "content": "teste"
            }
        ]
    )

    assert  resposta == "resposta-sucesso"

    assert (
        "principal" in router._instancias
    )

    assert (
        "fallback" not in router._instancias
    )

def test_fallback_provider_falha():

    router = ModelRouter()

    router.provider_principal = "principal"
    router.provider_fallback = "fallback"

    router._PROVIDERS = {
        "principal": ProviderFalha,
        "fallback": ProviderSucesso
    }

    resposta = router.gerar_resposta(
        mensagens=[
            {
                "role": "user",
                "content": "teste fallback"
            }
        ]
    )

    assert resposta == "resposta-sucesso"

    assert (
        "principal" in router._instancias
    )

    assert (
        "fallback" in router._instancias
    )


def test_router_falha_geral_provider():
    router = ModelRouter()

    router.provider_principal = "principal"
    router.provider_fallback = "fallback"

    router._PROVIDERS = {
        "principal": ProviderFalha,
        "fallback": ProviderFalha
    }

    with pytest.raises(
            RuntimeError
    ) as erro:
        router.gerar_resposta(
            mensagens=[
                {
                    "role": "user",
                    "content": "teste"
                }
            ]
        )

    mensagem = str(
        erro.value
    )

    assert "principal" in mensagem
    assert "fallback" in mensagem


def test_nao_repete_mesmo_provider_como_fallback():

    router = ModelRouter()

    router.provider_principal = "principal"
    router.provider_fallback = "fallback"

    router._PROVIDERS = {
        "principal": ProviderFalha,
    }

    with pytest.raises(RuntimeError):

        router.gerar_resposta(
            mensagens=[
                {
                    "role": "user",
                    "content": "teste"
                }
            ]
        )

        provider = (
            router._instancias["principal"]
        )

        assert provider.chamadas == 1