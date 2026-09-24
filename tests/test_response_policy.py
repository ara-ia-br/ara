from app.conversation.response_policy import (
    PoliticaMarkdown,
    ResponsePolicy,
    TamanhoResposta
)


def test_resposta_padrao_e_curta():

    perfil = ResponsePolicy.definir(
        "qual a capital do Japão?"
    )

    assert (
        perfil.tamanho
        == TamanhoResposta.CURTA
    )

    assert (
        perfil.markdown
        == PoliticaMarkdown.MINIMO
    )

    assert perfil.max_tokens == 350


def test_usuario_pode_pedir_resposta_ainda_mais_curta():

    perfil = ResponsePolicy.definir(
        "responda curto: o que é DNS?"
    )

    assert (
        perfil.tamanho
        == TamanhoResposta.CURTA
    )

    assert perfil.max_tokens == 220


def test_pergunta_tecnica_recebe_perfil_normal():

    perfil = ResponsePolicy.definir(
        "me explique esse erro do FastAPI"
    )

    assert (
        perfil.tamanho
        == TamanhoResposta.NORMAL
    )

    assert (
        perfil.markdown
        == PoliticaMarkdown.ESTRUTURADO
    )

    assert perfil.max_tokens == 1000


def test_codigo_e_detectado_como_contexto_tecnico():

    perfil = ResponsePolicy.definir(
        """
        def teste():
            return True
        """
    )

    assert (
        perfil.tamanho
        == TamanhoResposta.NORMAL
    )


def test_pedido_detalhado_tem_prioridade():

    perfil = ResponsePolicy.definir(
        "explique detalhadamente essa arquitetura "
        "FastAPI passo a passo"
    )

    assert (
        perfil.tamanho
        == TamanhoResposta.DETALHADA
    )

    assert perfil.max_tokens == 1400