from collections.abc import Callable

from app.agent.intent import (
    AgentDecision,
    AgentPlan,
)
from app.agent.plan_resolver import AgentPlanResolver


class AgentPlanExecutor:

    @staticmethod
    def executar(
        plano: AgentPlan,
        executar_passo: Callable[
            [AgentDecision, dict],
            object
        ],
    ) -> list[dict]:

        resultados: list[dict] = []

        for indice, passo in enumerate(
            plano.passos
        ):

            # ==========================================
            # VALIDA DEPENDÊNCIA
            # ==========================================

            if passo.depende_de is not None:

                if passo.depende_de < 0:
                    raise ValueError(
                        "Índice de dependência inválido."
                    )

                if passo.depende_de >= indice:
                    raise ValueError(
                        "Um passo só pode depender "
                        "de um passo anterior."
                    )

                if passo.depende_de >= len(
                    resultados
                ):
                    raise ValueError(
                        "Resultado da dependência "
                        "não está disponível."
                    )

            # ==========================================
            # RESOLVE ARGUMENTOS
            # ==========================================

            argumentos = (
                AgentPlanResolver
                .resolver_argumentos(
                    passo,
                    resultados
                )
            )

            # ==========================================
            # EXECUTA PASSO
            # ==========================================

            resultado = executar_passo(
                passo.decisao,
                argumentos
            )

            if not isinstance(
                resultado,
                dict
            ):
                raise ValueError(
                    "A execução de um passo do plano "
                    "deve retornar um dicionário."
                )

            resultados.append(
                resultado
            )

        return resultados
