from app.conversation.prompt_builder import PromptBuilder
from app.conversation.response_policy import ResponseProfile, TamanhoResposta, PoliticaMarkdown


def test_prompt_curto_prioriza_concisao():

    perfil = ResponseProfile(
        tamanho=TamanhoResposta.CURTA,
        markdown=PoliticaMarkdown.MINIMO,
        max_tokens=350,
        temperatura=0.5
    )

    prompt = (
        PromptBuilder.construir_politica(perfil)
    )

    assert "curta e direta" in prompt
    assert "1 a 3 frases" in prompt

def test_prompt_markdown_minimo():
    perfil = ResponseProfile(
        tamanho=TamanhoResposta.CURTA,
        markdown=PoliticaMarkdown.MINIMO,
        max_tokens=350,
        temperatura=0.5
    )

    prompt = (
        PromptBuilder.construir_politica(perfil)
    )

    assert (
        "Markdown somente quando realmente necessário"
        in prompt
    )

    assert "negrito" in prompt

def test_prompt_evitar_bordoes():
    perfil = ResponseProfile(
        tamanho=TamanhoResposta.NORMAL,
        markdown=PoliticaMarkdown.ESTRUTURADO,
        max_tokens=700,
        temperatura=0.4
    )

    prompt = (
        PromptBuilder.construir_politica(perfil)
    )

    assert "bordão fixo" in prompt
    assert "Fechou!" in prompt

def test_prompt_detalhado():
    perfil = ResponseProfile(
        tamanho=TamanhoResposta.DETALHADA,
        markdown=PoliticaMarkdown.ESTRUTURADO,
        max_tokens=1400,
        temperatura=0.45
    )

    prompt = (
        PromptBuilder.construir_politica(perfil)
    )

    assert (
        "resposta detalhada" in prompt
    )

    assert (
        "profundidade suficiente" in prompt
    )

def test_prompt_possui_tratamento_contextual():

    perfil = ResponseProfile(
        tamanho=TamanhoResposta.CURTA,
        markdown=PoliticaMarkdown.MINIMO,
        max_tokens=350,
        temperatura=0.5
    )

    prompt = (
        PromptBuilder.construir_politica(perfil)
    )

    assert (
        "Adapte o tratamento ao contexto" in prompt
    )

    assert (
        "Não finja possuir emoções humanas" in prompt
    )