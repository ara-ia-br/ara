import pytest

from app.agent.intent import (
    AgentDecision,
    AgentPlan,
    AgentPlanStep,
    TipoAcao,
)
from app.agent.plan_executor import (
    AgentPlanExecutor,
)


def test_executor_executa_plano_em_ordem():

    plano = AgentPlan(
        passos=[
            AgentPlanStep(
                decisao=AgentDecision(
                    acao=TipoAcao.EXECUTAR,
                    ferramenta="criar_tarefa",
                    argumentos={
                        "titulo": "Reunião",
                        "data_limite":
                            "2026-09-22T19:00:00",
                    },
                )
            ),
            AgentPlanStep(
                decisao=AgentDecision(
                    acao=TipoAcao.EXECUTAR,
                    ferramenta="criar_lembrete",
                    argumentos={},
                ),
                depende_de=0,
                resolver_argumentos={
                    "id_tarefa": {
                        "resultado_de": 0,
                        "campo": "id_tarefa",
                    },
                    "titulo": {
                        "resultado_de": 0,
                        "campo": "titulo",
                    },
                    "data_hora": {
                        "resultado_de": 0,
                        "campo": "data_limite",
                        "offset_minutos": -30,
                    },
                },
            ),
        ]
    )

    chamadas = []

    def executor_fake(
        decisao,
        argumentos
    ):

        chamadas.append(
            (
                decisao.ferramenta,
                argumentos.copy(),
            )
        )

        if (
            decisao.ferramenta
            == "criar_tarefa"
        ):
            return {
                "sucesso": True,
                "id_tarefa": 123,
                "titulo": "Reunião",
                "data_limite":
                    "2026-09-22T19:00:00",
            }

        if (
            decisao.ferramenta
            == "criar_lembrete"
        ):
            return {
                "sucesso": True,
                "id_lembrete": 456,
                "id_tarefa":
                    argumentos["id_tarefa"],
                "titulo":
                    argumentos["titulo"],
                "data_hora":
                    argumentos["data_hora"],
            }

        raise AssertionError(
            "Ferramenta inesperada."
        )

    resultados = (
        AgentPlanExecutor.executar(
            plano,
            executor_fake
        )
    )

    assert len(
        resultados
    ) == 2

    assert chamadas[0][0] == (
        "criar_tarefa"
    )

    assert chamadas[1][0] == (
        "criar_lembrete"
    )

    argumentos_lembrete = (
        chamadas[1][1]
    )

    assert (
        argumentos_lembrete[
            "id_tarefa"
        ]
        == 123
    )

    assert (
        argumentos_lembrete[
            "titulo"
        ]
        == "Reunião"
    )

    assert (
        argumentos_lembrete[
            "data_hora"
        ]
        == "2026-09-22T18:30:00"
    )


def test_executor_rejeita_dependencia_futura():

    plano = AgentPlan(
        passos=[
            AgentPlanStep(
                decisao=AgentDecision(
                    acao=TipoAcao.EXECUTAR,
                    ferramenta="teste",
                ),
                depende_de=1,
            )
        ]
    )

    with pytest.raises(
        ValueError
    ):
        AgentPlanExecutor.executar(
            plano,
            lambda decisao, argumentos: {}
        )


def test_executor_exige_resultado_dict():

    plano = AgentPlan(
        passos=[
            AgentPlanStep(
                decisao=AgentDecision(
                    acao=TipoAcao.EXECUTAR,
                    ferramenta="teste",
                )
            )
        ]
    )

    with pytest.raises(
        ValueError
    ):
        AgentPlanExecutor.executar(
            plano,
            lambda decisao, argumentos: None
        )
