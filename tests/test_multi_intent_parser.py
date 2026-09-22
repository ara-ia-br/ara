from app.agent.multi_intent_parser import MultiIntentParser


def test_divide_tarefa_e_lembrete():
    segmentos = MultiIntentParser.dividir(
        "crie uma tarefa chamada estudar amanhã às 19h "
        "e me lembre dela 30 minutos antes"
    )

    assert len(segmentos) == 2

    assert (segmentos[0].texto == "crie uma tarefa chamada estudar amanhã às 19h")

    assert (segmentos[1].texto == "me lembre dela 30 minutos antes")

    assert (segmentos[0].referencia_anterior is False)

    assert (segmentos[1].referencia_anterior is True)


def test_mensagem_simples_retorna_um_segmento():
    segmentos = MultiIntentParser.dividir("liste minhas tarefas")

    assert (segmentos[0].referencia_anterior is False)


def test_prioridade_nao_vira_segundo_intent():
    segmentos = MultiIntentParser.dividir("crie uma tarefa chamada estudar amanhã às 19h com prioridade alta")

    assert len(segmentos) == 1