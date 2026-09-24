from app.agent.agent import AraAgent


def _nao_deveria_resolver_contexto(*args, **kwargs):
    raise AssertionError(
        "O Agent tentou resolver contexto "
        "sem intenção operacional explícita."
    )


def test_observacao_contextual_nao_executa_mutacao(
    monkeypatch
):
    monkeypatch.setattr(
        AraAgent,
        "_resolver_tarefa_contextual",
        staticmethod(_nao_deveria_resolver_contexto)
    )

    decisao = (
        AraAgent._detectar_acao_contextual_tarefa(
            mensagem="está faltando o teste ARA",
            db=object(),
            id_usuario=1,
            id_conversa=1
        )
    )

    assert decisao is None


def test_faltando_tarefa_nao_executa_mutacao(
    monkeypatch
):
    monkeypatch.setattr(
        AraAgent,
        "_resolver_tarefa_contextual",
        staticmethod(_nao_deveria_resolver_contexto)
    )

    decisao = (
        AraAgent._detectar_acao_contextual_tarefa(
            mensagem="a tarefa está faltando",
            db=object(),
            id_usuario=1,
            id_conversa=1
        )
    )

    assert decisao is None


def test_faltando_reuniao_nao_executa_mutacao(
    monkeypatch
):
    monkeypatch.setattr(
        AraAgent,
        "_resolver_tarefa_contextual",
        staticmethod(_nao_deveria_resolver_contexto)
    )

    decisao = (
        AraAgent._detectar_acao_contextual_tarefa(
            mensagem="faltando a reunião",
            db=object(),
            id_usuario=1,
            id_conversa=1
        )
    )

    assert decisao is None