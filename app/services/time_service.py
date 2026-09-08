from datetime import datetime

from zoneinfo import ZoneInfo


class TimeService:

    TIMEZONE_PADRAO = "America/Sao_Paulo"

    @staticmethod
    def agora() -> datetime:

        timezone = ZoneInfo(
            TimeService.TIMEZONE_PADRAO
        )

        return datetime.now(
            timezone
        )


    @staticmethod
    def hoje():

        return (
            TimeService.agora()
            .date()
        )


    @staticmethod
    def iso() -> str:

        return (
            TimeService.agora()
            .isoformat()
        )


    @staticmethod
    def data_formatada() -> str:

        agora = TimeService.agora()

        return agora.strftime(
            "%d/%m/%Y"
        )


    @staticmethod
    def hora_formatada() -> str:

        agora = TimeService.agora()

        return agora.strftime(
            "%H:%M"
        )


    @staticmethod
    def contexto_temporal() -> str:

        agora = TimeService.agora()

        dias_semana = {
            0: "segunda-feira",
            1: "terça-feira",
            2: "quarta-feira",
            3: "quinta-feira",
            4: "sexta-feira",
            5: "sábado",
            6: "domingo"
        }

        dia_semana = dias_semana[
            agora.weekday()
        ]

        return (
            "CONTEXTO TEMPORAL ATUAL:\n"
            f"Data atual: {agora.strftime('%d/%m/%Y')}\n"
            f"Hora atual: {agora.strftime('%H:%M:%S')}\n"
            f"Dia da semana: {dia_semana}\n"
            f"Fuso horário: {TimeService.TIMEZONE_PADRAO}\n"
            f"Data/hora ISO: {agora.isoformat()}\n"
        )