from __future__ import annotations

from app.integrations.weather.base import (
    WeatherProvider,
)
from app.integrations.weather.met_norway_provider import (
    MetNorwayWeatherProvider,
)


class WeatherService:

    def __init__(
        self,
        provider: WeatherProvider | None = None,
    ):
        self.provider = (
            provider
            or MetNorwayWeatherProvider()
        )

    # =========================================================
    # CLIMA ATUAL
    # =========================================================

    async def obter_clima_atual(
        self,
        latitude: float,
        longitude: float,
    ) -> dict:

        self._validar_coordenadas(
            latitude,
            longitude,
        )

        clima = (
            await self.provider
            .obter_clima_atual(
                latitude=latitude,
                longitude=longitude,
            )
        )

        return {
            "latitude":
                clima.latitude,

            "longitude":
                clima.longitude,

            "temperatura_c":
                clima.temperature_c,

            "umidade_percentual":
                clima.humidity_percent,

            "vento_m_s":
                clima.wind_speed_mps,

            "direcao_vento_graus":
                clima.wind_direction_deg,

            "pressao_hpa":
                clima.air_pressure_hpa,

            "precipitacao_proxima_hora_mm":
                clima.precipitation_next_hour_mm,

            "condicao_codigo":
                clima.condition_code,

            "condicao":
                self._traduzir_condicao(
                    clima.condition_code
                ),

            "horario_previsao":
                clima.forecast_time.isoformat(),

            "fonte":
                clima.provider,

            "atribuicao":
                (
                    "Dados meteorológicos "
                    "fornecidos por MET Norway."
                ),
        }

    # =========================================================
    # VALIDAÇÃO
    # =========================================================

    @staticmethod
    def _validar_coordenadas(
        latitude: float,
        longitude: float,
    ):

        if not (
            -90
            <= float(latitude)
            <= 90
        ):
            raise ValueError(
                "Latitude inválida."
            )

        if not (
            -180
            <= float(longitude)
            <= 180
        ):
            raise ValueError(
                "Longitude inválida."
            )

    # =========================================================
    # TRADUÇÃO
    # =========================================================

    @classmethod
    def _traduzir_condicao(
        cls,
        codigo: str | None,
    ) -> str | None:

        if not codigo:
            return None

        codigo_base = (
            codigo
            .replace(
                "_day",
                "",
            )
            .replace(
                "_night",
                "",
            )
            .replace(
                "_polartwilight",
                "",
            )
        )

        traducoes = {
            "clearsky":
                "céu limpo",

            "fair":
                "tempo aberto",

            "partlycloudy":
                "parcialmente nublado",

            "cloudy":
                "nublado",

            "fog":
                "neblina",

            "lightrainshowers":
                "pancadas leves de chuva",

            "rainshowers":
                "pancadas de chuva",

            "heavyrainshowers":
                "pancadas fortes de chuva",

            "lightrain":
                "chuva leve",

            "rain":
                "chuva",

            "heavyrain":
                "chuva forte",

            "lightsleet":
                "chuva e neve leves",

            "sleet":
                "chuva e neve",

            "heavysleet":
                "chuva e neve intensas",

            "lightsnow":
                "neve leve",

            "snow":
                "neve",

            "heavysnow":
                "neve forte",

            "lightrainshowersandthunder":
                "pancadas leves com trovoadas",

            "rainshowersandthunder":
                "pancadas com trovoadas",

            "heavyrainshowersandthunder":
                "pancadas fortes com trovoadas",

            "lightsleetshowers":
                "pancadas leves de chuva e neve",

            "sleetshowers":
                "pancadas de chuva e neve",

            "heavysleetshowers":
                "pancadas fortes de chuva e neve",

            "lightsnowshowers":
                "pancadas leves de neve",

            "snowshowers":
                "pancadas de neve",

            "heavysnowshowers":
                "pancadas fortes de neve",
        }

        return traducoes.get(
            codigo_base,
            codigo_base,
        )


    async def obter_previsao_horaria(
        self,
        latitude: float,
        longitude: float,
        horas: int = 12
    ) -> list[dict]:

        if not -90 <= latitude <= 90:
            raise ValueError(
                "Latitude inválida."
            )

        if not -180 <= longitude <= 180:
            raise ValueError(
                "Longitude inválida."
            )

        snapshots = (
            await self.provider
            .obter_previsao_horaria(
                latitude=latitude,
                longitude=longitude,
                horas=horas
            )
        )

        previsoes = []

        for snapshot in snapshots:

            previsoes.append({
                "latitude":
                    snapshot.latitude,

                "longitude":
                    snapshot.longitude,

                "temperatura_c":
                    snapshot.temperature_c,

                "umidade_percentual":
                    snapshot.humidity_percent,

                "vento_m_s":
                    snapshot.wind_speed_mps,

                "direcao_vento_graus":
                    snapshot.wind_direction_deg,

                "pressao_hpa":
                    snapshot.air_pressure_hpa,

                "precipitacao_proxima_hora_mm":
                    snapshot
                    .precipitation_next_hour_mm,

                "condicao_codigo":
                    snapshot.condition_code,

                "condicao":
                    self._traduzir_condicao(
                        snapshot.condition_code
                    ),

                "horario_previsao":
                    snapshot
                    .forecast_time
                    .isoformat(),

                "fonte":
                    snapshot.provider,

                "atribuicao":
                    (
                        "Dados meteorológicos "
                        "fornecidos por MET Norway."
                    )
            })

        return previsoes


    async def obter_painel_clima(
        self,
        latitude: float,
        longitude: float,
        horas: int = 12
    ) -> dict:

        atual = await self.obter_clima_atual(
            latitude=latitude,
            longitude=longitude
        )

        previsao_horaria = (
            await self.obter_previsao_horaria(
                latitude=latitude,
                longitude=longitude,
                horas=horas
            )
        )

        return {
            "atual": atual,
            "horas": previsao_horaria
        }