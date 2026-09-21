from datetime import datetime, timedelta

from app.agent.intent import AgentPlanStep


class AgentPlanResolver:

    @staticmethod
    def resolver_argumentos(
        passo: AgentPlanStep,
        resultados: list[dict]
    ) -> dict:
        """
        Resolve os argumentos dinâmicos de uma etapa
        usando resultados de etapas anteriores.
        """

        argumentos = (
            passo.decisao.argumentos.copy()
            if passo.decisao.argumentos
            else {}
        )

        for nome_argumento, regra in (
            passo.resolver_argumentos.items()
        ):
            indice_resultado = regra.get(
                "resultado_de"
            )

            campo = regra.get(
                "campo"
            )

            if indice_resultado is None:
                raise ValueError(
                    f"Dependência inválida para "
                    f"'{nome_argumento}'."
                )

            if (
                indice_resultado < 0
                or indice_resultado >= len(resultados)
            ):
                raise ValueError(
                    f"Resultado da etapa "
                    f"{indice_resultado} não disponível."
                )

            resultado_origem = resultados[
                indice_resultado
            ]

            if not isinstance(
                resultado_origem,
                dict
            ):
                raise ValueError(
                    f"Resultado da etapa "
                    f"{indice_resultado} é inválido."
                )

            if campo not in resultado_origem:
                raise ValueError(
                    f"O campo '{campo}' não foi "
                    f"retornado na etapa "
                    f"{indice_resultado}."
                )

            valor = resultado_origem[
                campo
            ]

            # =============================================
            # TRANSFORMAÇÃO TEMPORAL
            # =============================================

            offset_minutos = regra.get(
                "offset_minutos"
            )

            if offset_minutos is not None:

                if not isinstance(valor, str):
                    raise ValueError(
                        f"O campo '{campo}' não possui "
                        f"uma data válida."
                    )

                try:
                    data = datetime.fromisoformat(
                        valor
                    )

                except ValueError as erro:
                    raise ValueError(
                        f"Não foi possível interpretar "
                        f"a data '{valor}'."
                    ) from erro

                data = (
                    data
                    + timedelta(
                        minutes=offset_minutos
                    )
                )

                valor = data.isoformat()

            # IMPORTANTE:
            # precisa permanecer DENTRO do for.
            argumentos[
                nome_argumento
            ] = valor

        return argumentos