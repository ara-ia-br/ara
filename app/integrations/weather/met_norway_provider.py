from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime

import httpx

from app.integrations.weather.base import (
    WeatherProvider,
    WeatherProviderError,
    WeatherSnapshot,
)


@dataclass(slots=True)
class _CacheEntry:
    snapshot: WeatherSnapshot
    expires_at: datetime
    last_modified: str | None


class MetNorwayWeatherProvider(WeatherProvider):
    BASE_URL = (
        "https://api.met.no/"
        "weatherapi/locationforecast/2.0/compact"
    )

    USER_AGENT = (
        "ARA/0.13 "
        "https://github.com/ara-ia-br/ara"
    )

    def __init__(
            self,
            timeout_seconds: float = 15.0,
    ):
        self.timeout_seconds = timeout_seconds

        self._cache: dict[
            tuple[float, float],
            _CacheEntry,
        ] = {}

    # =========================================================
    # API PRINCIPAL
    # =========================================================

    async def obter_clima_atual(
            self,
            latitude: float,
            longitude: float,
    ) -> WeatherSnapshot:

        latitude = round(
            float(latitude),
            4,
        )

        longitude = round(
            float(longitude),
            4,
        )

        chave = (
            latitude,
            longitude,
        )

        agora = datetime.now(
            timezone.utc
        )

        cache = self._cache.get(
            chave
        )

        if (
                cache
                and cache.expires_at > agora
        ):
            return cache.snapshot

        headers = {
            "User-Agent": self.USER_AGENT,
            "Accept": "application/json",
        }

        if (
                cache
                and cache.last_modified
        ):
            headers["If-Modified-Since"] = (
                cache.last_modified
            )

        params = {
            "lat": latitude,
            "lon": longitude,
        }

        try:

            async with httpx.AsyncClient(
                    timeout=self.timeout_seconds
            ) as client:

                response = await client.get(
                    self.BASE_URL,
                    params=params,
                    headers=headers,
                )

        except httpx.RequestError as erro:

            raise WeatherProviderError(
                "Não foi possível conectar "
                "ao serviço meteorológico."
            ) from erro

        # =====================================================
        # CACHE AINDA VÁLIDO NO SERVIDOR
        # =====================================================

        if (
                response.status_code == 304
                and cache
        ):
            cache.expires_at = (
                self._obter_expiracao(
                    response
                )
            )

            return cache.snapshot

        # =====================================================
        # RATE LIMIT
        # =====================================================

        if response.status_code == 429:
            raise WeatherProviderError(
                "O serviço meteorológico "
                "limitou temporariamente as requisições."
            )

        # =====================================================
        # ERROS EXTERNOS
        # =====================================================

        if response.status_code >= 400:
            raise WeatherProviderError(
                "Erro no serviço meteorológico "
                f"(HTTP {response.status_code})."
            )

        try:

            dados = response.json()

            timeseries = (
                dados
                .get("properties", {})
                .get("timeseries", [])
            )

            if not timeseries:
                raise WeatherProviderError(
                    "A previsão meteorológica "
                    "não retornou dados."
                )

            atual = timeseries[0]

            instante = (
                atual
                .get("data", {})
                .get("instant", {})
                .get("details", {})
            )

            proxima_hora = (
                atual
                .get("data", {})
                .get("next_1_hours", {})
            )

            resumo_proxima_hora = (
                proxima_hora
                .get("summary", {})
            )

            detalhes_proxima_hora = (
                proxima_hora
                .get("details", {})
            )

            horario = datetime.fromisoformat(
                atual["time"].replace(
                    "Z",
                    "+00:00",
                )
            )

            snapshot = WeatherSnapshot(
                latitude=latitude,
                longitude=longitude,

                temperature_c=instante.get(
                    "air_temperature"
                ),

                humidity_percent=instante.get(
                    "relative_humidity"
                ),

                wind_speed_mps=instante.get(
                    "wind_speed"
                ),

                wind_direction_deg=instante.get(
                    "wind_from_direction"
                ),

                air_pressure_hpa=instante.get(
                    "air_pressure_at_sea_level"
                ),

                precipitation_next_hour_mm=(
                    detalhes_proxima_hora.get(
                        "precipitation_amount"
                    )
                ),

                condition_code=(
                    resumo_proxima_hora.get(
                        "symbol_code"
                    )
                ),

                forecast_time=horario,

                provider="MET Norway",
            )

        except WeatherProviderError:
            raise

        except (
                KeyError,
                TypeError,
                ValueError,
        ) as erro:

            raise WeatherProviderError(
                "Resposta meteorológica "
                "em formato inesperado."
            ) from erro

        # =====================================================
        # CACHE
        # =====================================================

        self._cache[chave] = _CacheEntry(
            snapshot=snapshot,

            expires_at=(
                self._obter_expiracao(
                    response
                )
            ),

            last_modified=(
                response.headers.get(
                    "Last-Modified"
                )
            ),
        )

        return snapshot

    # =========================================================
    # EXPIRAÇÃO
    # =========================================================

    @staticmethod
    def _obter_expiracao(
            response: httpx.Response,
    ) -> datetime:

        expires = response.headers.get(
            "Expires"
        )

        if expires:

            try:

                data = parsedate_to_datetime(
                    expires
                )

                if data.tzinfo is None:
                    data = data.replace(
                        tzinfo=timezone.utc
                    )

                return data

            except (
                    TypeError,
                    ValueError,
            ):
                pass

        return (
                datetime.now(timezone.utc)
                + timedelta(minutes=10)
        )