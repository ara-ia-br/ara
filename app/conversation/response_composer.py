from datetime import datetime
from typing import Any


class ResponseComposer:

    @staticmethod
    def _formatar_data_hora(valor: Any) -> str | None:

        if valor is None:
            return None

        if isinstance(valor, datetime):
            data = valor
        else:
            texto = str(valor).strip()

            if not texto:
                return None

            try:
                data = datetime.fromisoformat(
                    texto.replace("Z", "+00:00")
                )
            except (ValueError, TypeError):
                return texto

        return data.strftime(
            "%d/%m/%Y às %H:%M"
        )

    @staticmethod
    def _formatar_status(
        status: Any
    ) -> str:

        mapa = {
            "PENDENTE": "pendente",
            "EM_ANDAMENTO": "em andamento",
            "CONCLUIDA": "concluída",
            "CANCELADA": "cancelada",
        }

        if status is None:
            return "desconhecido"

        texto = str(status)

        return mapa.get(
            texto,
            texto.lower()
        )

    @staticmethod
    def _formatar_prioridade(
        prioridade: Any
    ) -> str:

        prioridades = {
            1: "muito baixa",
            2: "baixa",
            3: "normal",
            4: "alta",
            5: "urgente",
        }

        try:
            prioridade_int = int(
                prioridade
            )
        except (
            TypeError,
            ValueError
        ):
            return str(prioridade)

        return prioridades.get(
            prioridade_int,
            str(prioridade_int)
        )

    @classmethod
    def compor(
        cls,
        ferramenta: str,
        resultado: dict
    ) -> str:

        if not isinstance(resultado, dict):
            return (
                "A ação foi concluída."
            )

        # =================================================
        # TAREFAS POR PERÍODO
        # =================================================

        if ferramenta == "listar_tarefas_periodo":

            tarefas = resultado.get(
                "tarefas",
                []
            )

            if not tarefas:
                return (
                    "Você não tem tarefas "
                    "nesse período."
                )

            linhas = [
                "Suas tarefas nesse período:"
            ]

            for tarefa in tarefas:

                titulo = tarefa.get(
                    "titulo",
                    "Sem título"
                )

                status = cls._formatar_status(
                    tarefa.get("status")
                )

                data_limite = (
                    cls._formatar_data_hora(
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

                linhas.append(linha)

            return "\n".join(linhas)

        # =================================================
        # LEMBRETES
        # =================================================

        if ferramenta == "excluir_todos_lembretes":

            quantidade = resultado.get(
                "quantidade_excluida",
                0
            )

            if quantidade == 0:
                return (
                    "Você não tinha lembretes "
                    "para excluir."
                )

            if quantidade == 1:
                return (
                    "Excluí 1 lembrete."
                )

            return (
                f"Excluí {quantidade} lembretes."
            )

        if ferramenta == "criar_lembrete":

            titulo = resultado.get(
                "titulo",
                "lembrete"
            )

            data_hora = (
                cls._formatar_data_hora(
                    resultado.get(
                        "data_hora"
                    )
                )
            )

            if data_hora:
                return (
                    f'Lembrete "{titulo}" criado '
                    f"para {data_hora}."
                )

            return (
                f'Lembrete "{titulo}" criado.'
            )

        if ferramenta == "listar_lembretes":

            lembretes = resultado.get(
                "lembretes",
                []
            )

            if not lembretes:
                return (
                    "Você não tem lembretes "
                    "pendentes no momento."
                )

            linhas = [
                "Seus lembretes pendentes:"
            ]

            for lembrete in lembretes:

                titulo = lembrete.get(
                    "titulo",
                    "Sem título"
                )

                data_hora = (
                    cls._formatar_data_hora(
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

            return "\n".join(linhas)

        if ferramenta == "editar_lembrete":

            titulo = resultado.get(
                "titulo",
                "lembrete"
            )

            data_hora = (
                cls._formatar_data_hora(
                    resultado.get(
                        "data_hora"
                    )
                )
            )

            if data_hora:
                return (
                    f'Lembrete "{titulo}" atualizado '
                    f"para {data_hora}."
                )

            return (
                f'Lembrete "{titulo}" atualizado.'
            )

        if ferramenta == "cancelar_lembrete":

            titulo = resultado.get(
                "titulo",
                "lembrete"
            )

            return (
                f'Lembrete "{titulo}" cancelado.'
            )

        if ferramenta == "concluir_lembrete":

            titulo = resultado.get(
                "titulo",
                "lembrete"
            )

            return (
                f'Lembrete "{titulo}" concluído.'
            )

        # =================================================
        # CONSULTA DE TAREFA
        # =================================================

        if ferramenta == "consultar_tarefa":

            titulo = resultado.get(
                "titulo",
                "tarefa"
            )

            campo = resultado.get(
                "campo_consultado"
            )

            if campo == "prioridade":

                prioridade = (
                    cls._formatar_prioridade(
                        resultado.get(
                            "prioridade"
                        )
                    )
                )

                return (
                    f'A tarefa "{titulo}" está com '
                    f"prioridade {prioridade}."
                )

            if campo == "status":

                status_original = (
                    resultado.get("status")
                )

                if not status_original:
                    return (
                        "Não consegui identificar "
                        f'o status da tarefa "{titulo}".'
                    )

                status = (
                    cls._formatar_status(
                        status_original
                    )
                )

                return (
                    f'A tarefa "{titulo}" está '
                    f"{status}."
                )

            if campo == "data_limite":

                data_limite = (
                    cls._formatar_data_hora(
                        resultado.get(
                            "data_limite"
                        )
                    )
                )

                if not data_limite:
                    return (
                        f'A tarefa "{titulo}" não '
                        "possui prazo definido."
                    )

                return (
                    f'O prazo da tarefa "{titulo}" '
                    f"é {data_limite}."
                )

            status = cls._formatar_status(
                resultado.get("status")
            )

            prioridade = (
                cls._formatar_prioridade(
                    resultado.get(
                        "prioridade"
                    )
                )
            )

            return (
                f'Tarefa "{titulo}": '
                f"status {status}, "
                f"prioridade {prioridade}."
            )

        # =================================================
        # TAREFAS
        # =================================================

        if ferramenta == "criar_tarefa":

            titulo = resultado.get(
                "titulo",
                "tarefa"
            )

            data_limite = (
                cls._formatar_data_hora(
                    resultado.get(
                        "data_limite"
                    )
                )
            )

            if data_limite:
                return (
                    f'Tarefa "{titulo}" criada '
                    f"para {data_limite}."
                )

            return (
                f'Tarefa "{titulo}" criada.'
            )

        if ferramenta == "editar_tarefa":

            titulo = resultado.get(
                "titulo",
                "tarefa"
            )

            return (
                f'Tarefa "{titulo}" atualizada.'
            )

        if ferramenta == "listar_tarefas":

            tarefas = resultado.get(
                "tarefas",
                []
            )

            if not tarefas:
                return (
                    "Você ainda não tem tarefas."
                )

            linhas = [
                "Suas tarefas:"
            ]

            for tarefa in tarefas:

                titulo = tarefa.get(
                    "titulo",
                    "Sem título"
                )

                status = (
                    cls._formatar_status(
                        tarefa.get("status")
                    )
                )

                linhas.append(
                    f"- {titulo} ({status})"
                )

            return "\n".join(linhas)

        if ferramenta == "iniciar_tarefa":

            titulo = resultado.get(
                "titulo",
                "tarefa"
            )

            return (
                f'A tarefa "{titulo}" está '
                "em andamento."
            )

        if ferramenta == "concluir_tarefa":

            titulo = resultado.get(
                "titulo",
                "tarefa"
            )

            return (
                f'A tarefa "{titulo}" foi concluída.'
            )

        if ferramenta == "cancelar_tarefa":

            titulo = resultado.get(
                "titulo",
                "tarefa"
            )

            return (
                f'A tarefa "{titulo}" foi cancelada.'
            )

        if ferramenta == "reabrir_tarefa":

            titulo = resultado.get(
                "titulo",
                "tarefa"
            )

            return (
                f'A tarefa "{titulo}" foi reaberta '
                "e voltou para pendente."
            )

        # =================================================
        # FALLBACK
        # =================================================

        return (
            "A ação foi concluída."
        )