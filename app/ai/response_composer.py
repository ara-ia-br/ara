import random
from datetime import datetime


class ResponseComposer:

    # =========================================================
    # HELPERS
    # =========================================================

    @staticmethod
    def _formatar_data_hora(
        valor: str | None
    ) -> str | None:

        if not valor:
            return None

        try:

            data = datetime.fromisoformat(
                valor
            )

            return data.strftime(
                "%d/%m/%Y às %H:%M"
            )

        except (
            ValueError,
            TypeError
        ):
            return str(valor)


    @staticmethod
    def _formatar_status(
        status: str | None
    ) -> str:

        if not status:
            return "desconhecido"

        status_formatados = {
            "PENDENTE": "pendente",
            "EM_ANDAMENTO": "em andamento",
            "CONCLUIDA": "concluída",
            "CONCLUIDO": "concluído",
            "CANCELADA": "cancelada",
            "CANCELADO": "cancelado",
        }

        return status_formatados.get(
            str(status).upper(),
            str(status).lower()
        )


    @staticmethod
    def _formatar_prioridade(
        prioridade
    ) -> str:

        prioridades = {
            1: "muito baixa",
            2: "baixa",
            3: "normal",
            4: "alta",
            5: "urgente"
        }

        return prioridades.get(
            prioridade,
            str(prioridade)
        )


    # =========================================================
    # MÉTODO PRINCIPAL
    # =========================================================

    @staticmethod
    def formatar_tool(
        ferramenta: str,
        resultado: dict
    ) -> str:

        if not isinstance(resultado, dict):

            return (
                "A operação foi executada, mas não consegui "
                "interpretar corretamente o resultado."
            )

        # =====================================================
        # LISTAR TAREFAS POR PERÍODO
        # =====================================================

        if ferramenta == "listar_tarefas_periodo":

            tarefas = resultado.get(
                "tarefas",
                []
            )

            if not tarefas:

                return (
                    "Você não tem nenhuma tarefa "
                    "nesse período."
                )

            linhas = [
                "Suas tarefas nesse período:"
            ]

            for tarefa in tarefas:

                titulo = tarefa.get(
                    "titulo",
                    "Tarefa"
                )

                status = (
                    ResponseComposer
                    ._formatar_status(
                        tarefa.get("status")
                    )
                )

                data_limite = (
                    ResponseComposer
                    ._formatar_data_hora(
                        tarefa.get(
                            "data_limite"
                        )
                    )
                )

                linha = (
                    f"- {titulo} ({status})"
                )

                if data_limite:
                    linha += (
                        f" — {data_limite}"
                    )

                linhas.append(
                    linha
                )

            return "\n".join(
                linhas
            )


        # =====================================================
        # LEMBRETES
        # =====================================================

        if ferramenta == "excluir_todos_lembretes":

            quantidade = resultado.get(
                "quantidade_excluida",
                0
            )

            if quantidade == 0:

                return (
                    "Você não tinha nenhum lembrete "
                    "para excluir."
                )

            if quantidade == 1:

                return (
                    "Pronto! Excluí 1 lembrete."
                )

            return (
                f"Pronto! Excluí "
                f"{quantidade} lembretes."
            )


        # =====================================================
        # CRIAR LEMBRETE
        # =====================================================

        if ferramenta == "criar_lembrete":

            aberturas = [
                "Fechou!",
                "Beleza!",
                "Boa!",
                "Tranquilo!",
                "Pronto!",
                "Certo!",
                "Show!",
                "Combinado!"
            ]

            abertura = random.choice(
                aberturas
            )

            titulo = resultado.get(
                "titulo",
                "Lembrete"
            )

            data_hora = (
                ResponseComposer
                ._formatar_data_hora(
                    resultado.get(
                        "data_hora"
                    )
                )
            )

            if data_hora:

                return (
                    f'{abertura} Criei o lembrete '
                    f'de "{titulo}" '
                    f'para {data_hora}.'
                )

            return (
                f'{abertura} Criei o lembrete '
                f'de "{titulo}".'
            )


        # =====================================================
        # LISTAR LEMBRETES
        # =====================================================

        if ferramenta == "listar_lembretes":

            lembretes = resultado.get(
                "lembretes",
                []
            )

            if not lembretes:

                return (
                    "Você não tem nenhum lembrete "
                    "pendente no momento."
                )

            linhas = [
                "Seus lembretes pendentes:"
            ]

            for lembrete in lembretes:

                titulo = lembrete.get(
                    "titulo",
                    "Lembrete"
                )

                data_hora = (
                    ResponseComposer
                    ._formatar_data_hora(
                        lembrete.get(
                            "data_hora"
                        )
                    )
                )

                if data_hora:

                    linhas.append(
                        f"- {titulo} — "
                        f"{data_hora}"
                    )

                else:

                    linhas.append(
                        f"- {titulo}"
                    )

            return "\n".join(
                linhas
            )


        # =====================================================
        # CONSULTAR LEMBRETE
        # =====================================================

        if ferramenta == "consultar_lembrete":

            titulo = resultado.get(
                "titulo",
                "Lembrete"
            )

            data_hora = (
                ResponseComposer
                ._formatar_data_hora(
                    resultado.get(
                        "data_hora"
                    )
                )
            )

            status = (
                ResponseComposer
                ._formatar_status(
                    resultado.get(
                        "status"
                    )
                )
            )

            if data_hora:

                return (
                    f"O lembrete '{titulo}' está "
                    f"{status} e está marcado para "
                    f"{data_hora}."
                )

            return (
                f"O lembrete '{titulo}' está "
                f"{status}."
            )


        # =====================================================
        # EDITAR LEMBRETE
        # =====================================================

        if ferramenta == "editar_lembrete":

            titulo = resultado.get(
                "titulo",
                "Lembrete"
            )

            data_hora = (
                ResponseComposer
                ._formatar_data_hora(
                    resultado.get(
                        "data_hora"
                    )
                )
            )

            if data_hora:

                return (
                    f"Fechou! Atualizei o lembrete "
                    f"'{titulo}' para "
                    f"{data_hora}."
                )

            return (
                f"Fechou! Atualizei o lembrete "
                f"'{titulo}'."
            )


        # =====================================================
        # CANCELAR LEMBRETE
        # =====================================================

        if ferramenta == "cancelar_lembrete":

            titulo = resultado.get(
                "titulo",
                "Lembrete"
            )

            return (
                f"Fechou! Cancelei o lembrete "
                f"'{titulo}'."
            )


        # =====================================================
        # CONCLUIR LEMBRETE
        # =====================================================

        if ferramenta == "concluir_lembrete":

            titulo = resultado.get(
                "titulo",
                "Lembrete"
            )

            return (
                f"Boa! Marquei o lembrete "
                f"'{titulo}' como concluído."
            )


        # =====================================================
        # TAREFAS
        # =====================================================

        if ferramenta == "consultar_tarefa":

            titulo = resultado.get(
                "titulo",
                "tarefa"
            )

            campo = resultado.get(
                "campo_consultado"
            )

            # -------------------------------------------------
            # PRIORIDADE
            # -------------------------------------------------

            if campo == "prioridade":

                prioridade = resultado.get(
                    "prioridade"
                )

                prioridade_formatada = (
                    ResponseComposer
                    ._formatar_prioridade(
                        prioridade
                    )
                )

                return (
                    f"A tarefa '{titulo}' está com "
                    f"prioridade "
                    f"{prioridade_formatada}."
                )

            # -------------------------------------------------
            # STATUS
            # -------------------------------------------------

            if campo == "status":

                status = (
                    ResponseComposer
                    ._formatar_status(
                        resultado.get(
                            "status"
                        )
                    )
                )

                return (
                    f"A tarefa '{titulo}' está "
                    f"{status}."
                )

            # -------------------------------------------------
            # PRAZO
            # -------------------------------------------------

            if campo == "data_limite":

                data_limite = resultado.get(
                    "data_limite"
                )

                if not data_limite:

                    return (
                        f"A tarefa '{titulo}' não possui "
                        f"prazo definido."
                    )

                data_formatada = (
                    ResponseComposer
                    ._formatar_data_hora(
                        data_limite
                    )
                )

                return (
                    f"O prazo da tarefa '{titulo}' é "
                    f"{data_formatada}."
                )

            # -------------------------------------------------
            # CONSULTA GERAL
            # -------------------------------------------------

            status = (
                ResponseComposer
                ._formatar_status(
                    resultado.get(
                        "status"
                    )
                )
            )

            prioridade = (
                ResponseComposer
                ._formatar_prioridade(
                    resultado.get(
                        "prioridade"
                    )
                )
            )

            return (
                f"Tarefa '{titulo}': "
                f"status {status}, "
                f"prioridade {prioridade}."
            )


        # =====================================================
        # CRIAR TAREFA
        # =====================================================

        if ferramenta == "criar_tarefa":

            titulo = resultado.get(
                "titulo",
                "Tarefa"
            )

            return (
                f"Fechou! Criei a tarefa "
                f"'{titulo}'."
            )


        # =====================================================
        # EDITAR TAREFA
        # =====================================================

        if ferramenta == "editar_tarefa":

            titulo = resultado.get(
                "titulo",
                "Tarefa"
            )

            return (
                f"Fechou! Atualizei a tarefa "
                f"'{titulo}'."
            )


        # =====================================================
        # LISTAR TAREFAS
        # =====================================================

        if ferramenta == "listar_tarefas":

            tarefas = resultado.get(
                "tarefas",
                []
            )

            if not tarefas:

                return (
                    "Você ainda não tem nenhuma tarefa."
                )

            linhas = [
                "Suas tarefas:"
            ]

            for tarefa in tarefas:

                titulo = tarefa.get(
                    "titulo",
                    "Tarefa"
                )

                status = (
                    ResponseComposer
                    ._formatar_status(
                        tarefa.get(
                            "status"
                        )
                    )
                )

                linhas.append(
                    f"- {titulo} ({status})"
                )

            return "\n".join(
                linhas
            )


        # =====================================================
        # INICIAR TAREFA
        # =====================================================

        if ferramenta == "iniciar_tarefa":

            titulo = resultado.get(
                "titulo",
                "Tarefa"
            )

            return (
                f"Boa! A tarefa "
                f"'{titulo}' agora está "
                f"em andamento."
            )


        # =====================================================
        # CONCLUIR TAREFA
        # =====================================================

        if ferramenta == "concluir_tarefa":

            titulo = resultado.get(
                "titulo",
                "Tarefa"
            )

            return (
                f"Boa! Marquei a tarefa "
                f"'{titulo}' como concluída."
            )


        # =====================================================
        # CANCELAR TAREFA
        # =====================================================

        if ferramenta == "cancelar_tarefa":

            titulo = resultado.get(
                "titulo",
                "Tarefa"
            )

            return (
                f"Fechou! Cancelei a tarefa "
                f"'{titulo}'."
            )


        # =====================================================
        # REABRIR TAREFA
        # =====================================================

        if ferramenta == "reabrir_tarefa":

            titulo = resultado.get(
                "titulo",
                "Tarefa"
            )

            return (
                f"Fechou! Reabri a tarefa "
                f"'{titulo}'. "
                f"Ela voltou para pendente."
            )


        # =====================================================
        # CLIMA
        # =====================================================

        if ferramenta == "consultar_clima_local":

            if resultado.get("sucesso") is False:
                return (
                    resultado.get(
                        "erro",
                        "Não consegui consultar o clima "
                        "neste momento."
                    )
                )

            local = (
                resultado.get("local")
                or {}
            )

            clima = (
                resultado.get("clima")
                or {}
            )

            nome_local = (
                local.get("cidade")
                or local.get("nome")
                or local.get("nome_completo")
                or "essa localização"
            )

            temperatura = clima.get(
                "temperatura_c"
            )

            condicao = clima.get(
                "condicao"
            )

            umidade = clima.get(
                "umidade_percentual"
            )

            vento = clima.get(
                "vento_m_s"
            )

            precipitacao = clima.get(
                "precipitacao_proxima_hora_mm"
            )

            partes = []

            # -------------------------------------------------
            # TEMPERATURA + CONDIÇÃO
            # -------------------------------------------------

            if (
                temperatura is not None
                and condicao
            ):
                partes.append(
                    f"Em {nome_local}, está fazendo "
                    f"{temperatura:.1f} °C, "
                    f"com {condicao}."
                )

            elif temperatura is not None:

                partes.append(
                    f"Em {nome_local}, a temperatura "
                    f"está em {temperatura:.1f} °C."
                )

            elif condicao:

                partes.append(
                    f"Em {nome_local}, o tempo está "
                    f"{condicao}."
                )

            # -------------------------------------------------
            # UMIDADE
            # -------------------------------------------------

            if umidade is not None:

                partes.append(
                    f"A umidade está em "
                    f"{umidade:.0f}%."
                )

            # -------------------------------------------------
            # VENTO
            # -------------------------------------------------

            if vento is not None:

                partes.append(
                    f"O vento está em "
                    f"{vento:.1f} m/s."
                )

            # -------------------------------------------------
            # PRECIPITAÇÃO
            # -------------------------------------------------

            if precipitacao is not None:

                if precipitacao <= 0:

                    partes.append(
                        "Não há precipitação prevista "
                        "para a próxima hora."
                    )

                else:

                    partes.append(
                        f"A previsão indica cerca de "
                        f"{precipitacao:.1f} mm de chuva "
                        f"na próxima hora."
                    )

            if not partes:

                return (
                    f"Consultei o clima de {nome_local}, "
                    f"mas não recebi dados meteorológicos "
                    f"suficientes para montar a resposta."
                )

            return " ".join(
                partes
            )


        # =====================================================
        # FALLBACK DE TOOL
        # =====================================================

        return (
            "A ação foi executada com sucesso."
        )