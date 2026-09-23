from app.agent.multi_intent_parser import (
    MultiIntentParser,
)


def test_divide_tarefa_e_lembrete():

    segmentos = MultiIntentParser.dividir(
        "crie uma tarefa chamada estudar amanhã às 19h "
        "e me lembre dela 30 minutos antes"
    )

    assert len(segmentos) == 2

    assert (
        segmentos[0].texto
        == "crie uma tarefa chamada estudar amanhã às 19h"
    )

    assert (
        segmentos[1].texto
        == "me lembre dela 30 minutos antes"
    )

    assert segmentos[0].referencia_anterior is False
    assert segmentos[1].referencia_anterior is True


def test_mensagem_simples_retorna_um_segmento():

    segmentos = MultiIntentParser.dividir(
        "liste minhas tarefas"
    )

    assert len(segmentos) == 1

    assert (
        segmentos[0].texto
        == "liste minhas tarefas"
    )


def test_prioridade_nao_vira_segundo_intent():

    segmentos = MultiIntentParser.dividir(
        "crie uma tarefa chamada estudar amanhã às 19h "
        "com prioridade alta"
    )

    assert len(segmentos) == 1


def test_duas_acoes_independentes():

    segmentos = MultiIntentParser.dividir(
        "liste minhas tarefas e liste meus lembretes"
    )

    assert len(segmentos) == 2

    assert segmentos[0].texto == "liste minhas tarefas"
    assert segmentos[1].texto == "liste meus lembretes"

    assert segmentos[1].referencia_anterior is False


def test_tres_intents():

    segmentos = MultiIntentParser.dividir(
        "liste minhas tarefas "
        "e liste meus lembretes "
        "e crie uma tarefa chamada estudar"
    )

    assert len(segmentos) == 3

    assert segmentos[0].texto == "liste minhas tarefas"
    assert segmentos[1].texto == "liste meus lembretes"
    assert (
        segmentos[2].texto
        == "crie uma tarefa chamada estudar"
    )


def test_nao_quebra_titulo_com_e():

    segmentos = MultiIntentParser.dividir(
        "crie uma tarefa chamada estudar e revisar amanhã"
    )

    assert len(segmentos) == 1


def test_referencia_contextual_no_segundo_segmento():

    segmentos = MultiIntentParser.dividir(
        "crie uma tarefa chamada reunião amanhã às 19h "
        "e me lembre dessa tarefa 1 hora antes"
    )

    assert len(segmentos) == 2
    assert segmentos[1].referencia_anterior is True




def test_listagem_compartilhada_tarefas_e_lembretes():

    segmentos = MultiIntentParser.dividir(
        "liste minhas tarefas e meus lembretes"
    )

    assert len(segmentos) == 2

    assert (
        segmentos[0].texto
        == "liste minhas tarefas"
    )

    assert (
        segmentos[1].texto
        == "liste meus lembretes"
    )


def test_listagem_compartilhada_sem_possessivo():

    segmentos = MultiIntentParser.dividir(
        "lista minhas tarefas e lembretes"
    )

    assert len(segmentos) == 2

    assert (
        segmentos[0].texto
        == "liste minhas tarefas"
    )

    assert (
        segmentos[1].texto
        == "liste meus lembretes"
    )


def test_listagem_tolera_tarefa_no_singular():

    segmentos = MultiIntentParser.dividir(
        "lista minhas tarefa e meus lembretes"
    )

    assert len(segmentos) == 2

    assert (
        segmentos[0].texto
        == "liste minhas tarefas"
    )

    assert (
        segmentos[1].texto
        == "liste meus lembretes"
    )


def test_listagem_compartilhada_ordem_inversa():

    segmentos = MultiIntentParser.dividir(
        "liste meus lembretes e minhas tarefas"
    )

    assert len(segmentos) == 2

    assert (
        segmentos[0].texto
        == "liste meus lembretes"
    )

    assert (
        segmentos[1].texto
        == "liste minhas tarefas"
    )