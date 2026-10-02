from __future__ import annotations

from dataclasses import dataclass
from datetime import (
    datetime,
    timedelta,
    timezone
)
from email.utils import (
    parsedate_to_datetime
)

import httpx

from app.integrations.weather.base import (
    WeatherProvider,
    WeatherProviderError,
    WeatherSnapshot
)


@dataclass(
    slots=True
)
class _CacheEntry:
    payload: dict
    expires_at: datetime
    last_modified: str | None


class MetNorwayWeatherProvider(
    WeatherProvider
):

    BASE_URL = (
        "https://api.met.no/"
        "weatherapi/locationforecast/"
        "2.0/compact"
    )

    USER_AGENT = (
        "ARA/0.13 "
        "https://github.com/ara-ia-br/ara"
    )

    FALLBACK_CACHE_MINUTES = 10


    def __init__(
        self
    ):

        self._cache: dict[
            tuple[float, float],
            _CacheEntry
        ] = {}


    # =========================================================
    # COORDENADAS
    # =========================================================

    @staticmethod
    def _normalizar_coordenadas(
        latitude: float,
        longitude: float
    ) -> tuple[float, float]:

        return (
            round(
                float(latitude),
                4
            ),
            round(
                float(longitude),
                4
            )
        )


    # =========================================================
    # DATAS
    # =========================================================

    @staticmethod
    def _parse_data_http(
        valor: str | None
    ) -> datetime | None:

        if not valor:
            return None

        try:

            data = (
                parsedate_to_datetime(
                    valor
                )
            )

            if data.tzinfo is None:

                data = data.replace(
                    tzinfo=timezone.utc
                )

            return data.astimezone(
                timezone.utc
            )

        except (
            TypeError,
            ValueError
        ):

            return None


    @staticmethod
    def _parse_iso_datetime(
        valor: str
    ) -> datetime:

        return datetime.fromisoformat(
            valor.replace(
                "Z",
                "+00:00"
            )
        )


    # =========================================================
    # CONVERSÃO NUMÉRICA
    # =========================================================

    @staticmethod
    def _valor_float(
        valor
    ) -> float | None:

        if valor is None:
            return None

        try:

            return float(
                valor
            )

        except (
            TypeError,
            ValueError
        ):

            return None


    # =========================================================
    # HTTP + CACHE
    # =========================================================

    async def _obter_payload(
        self,
        latitude: float,
        longitude: float
    ) -> dict:

        (
            latitude,
            longitude
        ) = (
            self._normalizar_coordenadas(
                latitude,
                longitude
            )
        )

        chave = (
            latitude,
            longitude
        )

        agora = datetime.now(
            timezone.utc
        )

        cache = self._cache.get(
            chave
        )


        # -----------------------------------------------------
        # CACHE VÁLIDO
        # -----------------------------------------------------

        if (
            cache is not None
            and agora
            < cache.expires_at
        ):

            return cache.payload


        # -----------------------------------------------------
        # HEADERS
        # -----------------------------------------------------

        headers = {
            "User-Agent":
                self.USER_AGENT
        }


        if (
            cache is not None
            and cache.last_modified
        ):

            headers[
                "If-Modified-Since"
            ] = (
                cache.last_modified
            )


        params = {
            "lat": latitude,
            "lon": longitude
        }


        # -----------------------------------------------------
        # REQUEST
        # -----------------------------------------------------

        try:

            async with (
                httpx.AsyncClient(
                    timeout=15.0
                )
                as cliente
            ):

                resposta = (
                    await cliente.get(
                        self.BASE_URL,
                        params=params,
                        headers=headers
                    )
                )

        except httpx.HTTPError as erro:

            raise WeatherProviderError(
                "Não consegui acessar "
                "o serviço meteorológico."
            ) from erro


        # -----------------------------------------------------
        # 304
        # -----------------------------------------------------

        if (
            resposta.status_code
            == 304
        ):

            if cache is None:

                raise WeatherProviderError(
                    "O serviço meteorológico "
                    "retornou cache inválido."
                )


            expiracao = (
                self._parse_data_http(
                    resposta.headers.get(
                        "Expires"
                    )
                )
                or (
                    agora
                    + timedelta(
                        minutes=
                            self
                            .FALLBACK_CACHE_MINUTES
                    )
                )
            )

            cache.expires_at = (
                expiracao
            )

            return cache.payload


        # -----------------------------------------------------
        # RATE LIMIT
        # -----------------------------------------------------

        if (
            resposta.status_code
            == 429
        ):

            raise WeatherProviderError(
                "O serviço meteorológico "
                "está temporariamente "
                "limitando consultas."
            )


        # -----------------------------------------------------
        # ERRO HTTP
        # -----------------------------------------------------

        if (
            resposta.status_code
            >= 400
        ):

            raise WeatherProviderError(
                "O serviço meteorológico "
                "retornou HTTP "
                f"{resposta.status_code}."
            )


        # -----------------------------------------------------
        # JSON
        # -----------------------------------------------------

        try:

            payload = (
                resposta.json()
            )

        except ValueError as erro:

            raise WeatherProviderError(
                "O serviço meteorológico "
                "retornou dados inválidos."
            ) from erro


        if not isinstance(
            payload,
            dict
        ):

            raise WeatherProviderError(
                "Resposta meteorológica "
                "inválida."
            )


        # -----------------------------------------------------
        # EXPIRAÇÃO
        # -----------------------------------------------------

        expiracao = (
            self._parse_data_http(
                resposta.headers.get(
                    "Expires"
                )
            )
            or (
                agora
                + timedelta(
                    minutes=
                        self
                        .FALLBACK_CACHE_MINUTES
                )
            )
        )


        if expiracao <= agora:

            expiracao = (
                agora
                + timedelta(
                    minutes=
                        self
                        .FALLBACK_CACHE_MINUTES
                )
            )


        # -----------------------------------------------------
        # SALVA CACHE
        # -----------------------------------------------------

        self._cache[
            chave
        ] = _CacheEntry(

            payload=payload,

            expires_at=
                expiracao,

            last_modified=
                resposta.headers.get(
                    "Last-Modified"
                )
        )


        return payload


    # =========================================================
    # TIMESERIES
    # =========================================================

    @staticmethod
    def _obter_timeseries(
        payload: dict
    ) -> list[dict]:

        try:

            timeseries = (
                payload[
                    "properties"
                ][
                    "timeseries"
                ]
            )

        except (
            KeyError,
            TypeError
        ) as erro:

            raise WeatherProviderError(
                "Previsão meteorológica "
                "sem série temporal."
            ) from erro


        if (
            not isinstance(
                timeseries,
                list
            )
            or not timeseries
        ):

            raise WeatherProviderError(
                "O serviço meteorológico "
                "não retornou previsões."
            )


        return timeseries


    # =========================================================
    # ITEM → SNAPSHOT
    # =========================================================

    def _converter_item(
        self,
        item: dict,
        latitude: float,
        longitude: float
    ) -> WeatherSnapshot:

        try:

            horario = (
                self._parse_iso_datetime(
                    item["time"]
                )
            )

            dados = (
                item["data"]
            )

            detalhes = (
                dados
                .get(
                    "instant",
                    {}
                )
                .get(
                    "details",
                    {}
                )
            )

        except (
            KeyError,
            TypeError,
            ValueError
        ) as erro:

            raise WeatherProviderError(
                "Item de previsão "
                "meteorológica inválido."
            ) from erro


        # -----------------------------------------------------
        # PRÓXIMA HORA
        # -----------------------------------------------------

        proxima_hora = (
            dados.get(
                "next_1_hours"
            )
            or {}
        )


        resumo = (
            proxima_hora.get(
                "summary",
                {}
            )
        )


        detalhes_proxima_hora = (
            proxima_hora.get(
                "details",
                {}
            )
        )


        codigo_condicao = (
            resumo.get(
                "symbol_code"
            )
        )


        # -----------------------------------------------------
        # FALLBACK CONDIÇÃO
        # -----------------------------------------------------

        if not codigo_condicao:

            for chave in (
                "next_6_hours",
                "next_12_hours"
            ):

                bloco = (
                    dados.get(
                        chave
                    )
                    or {}
                )

                codigo_condicao = (
                    bloco
                    .get(
                        "summary",
                        {}
                    )
                    .get(
                        "symbol_code"
                    )
                )

                if codigo_condicao:
                    break


        precipitacao = (
            detalhes_proxima_hora
            .get(
                "precipitation_amount"
            )
        )


        return WeatherSnapshot(

            latitude=
                float(latitude),

            longitude=
                float(longitude),

            temperature_c=
                self._valor_float(
                    detalhes.get(
                        "air_temperature"
                    )
                ),

            humidity_percent=
                self._valor_float(
                    detalhes.get(
                        "relative_humidity"
                    )
                ),

            wind_speed_mps=
                self._valor_float(
                    detalhes.get(
                        "wind_speed"
                    )
                ),

            wind_direction_deg=
                self._valor_float(
                    detalhes.get(
                        "wind_from_direction"
                    )
                ),

            air_pressure_hpa=
                self._valor_float(
                    detalhes.get(
                        "air_pressure_at_sea_level"
                    )
                ),

            precipitation_next_hour_mm=
                self._valor_float(
                    precipitacao
                ),

            condition_code=
                codigo_condicao,

            forecast_time=
                horario,

            provider=
                "MET Norway"
        )


    # =========================================================
    # CLIMA ATUAL
    # =========================================================

    async def obter_clima_atual(
        self,
        latitude: float,
        longitude: float
    ) -> WeatherSnapshot:

        payload = (
            await self._obter_payload(
                latitude,
                longitude
            )
        )


        timeseries = (
            self._obter_timeseries(
                payload
            )
        )


        return self._converter_item(
            timeseries[0],
            latitude,
            longitude
        )


    # =========================================================
    # PREVISÃO HORÁRIA
    # =========================================================

    async def obter_previsao_horaria(
        self,
        latitude: float,
        longitude: float,
        horas: int = 12
    ) -> list[WeatherSnapshot]:

        if horas < 1:

            raise ValueError(
                "A quantidade de horas "
                "deve ser maior que zero."
            )


        # Card da A.R.A. não precisa
        # carregar mais que 24 pontos.
        horas = min(
            horas,
            24
        )


        payload = (
            await self._obter_payload(
                latitude,
                longitude
            )
        )


        timeseries = (
            self._obter_timeseries(
                payload
            )
        )


        agora = datetime.now(
            timezone.utc
        )


        previsoes: list[
            WeatherSnapshot
        ] = []


        for item in timeseries:

            try:

                horario = (
                    self
                    ._parse_iso_datetime(
                        item["time"]
                    )
                )

            except (
                KeyError,
                TypeError,
                ValueError
            ):

                continue


            # Inclui a hora meteorológica
            # atual com tolerância.
            if (
                horario
                <
                (
                    agora
                    - timedelta(
                        minutes=59
                    )
                )
            ):

                continue


            previsoes.append(

                self._converter_item(
                    item,
                    latitude,
                    longitude
                )
            )


            if (
                len(previsoes)
                >= horas
            ):

                break


        if not previsoes:

            raise WeatherProviderError(
                "Não encontrei previsão "
                "horária para essa "
                "localização."
            )


        return previsoes