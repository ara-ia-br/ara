from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

import httpx

from app.integrations.geocoding.base import (
    GeocodingProvider,
    GeocodingProviderError,
    LocationResult,
)


@dataclass(slots=True)
class _GeocodingCacheEntry:
    resultados: list[LocationResult]
    expires_at: datetime


class NominatimGeocodingProvider(
    GeocodingProvider
):

    BASE_URL = (
        "https://nominatim.openstreetmap.org/search"
    )

    USER_AGENT = (
        "ARA/0.13 "
        "https://github.com/ara-ia-br/ara"
    )

    CACHE_DURATION = timedelta(
        days=7
    )

    MIN_REQUEST_INTERVAL = 1.05

    def __init__(
        self,
        timeout_seconds: float = 15.0,
    ):
        self.timeout_seconds = timeout_seconds

        self._cache: dict[
            str,
            _GeocodingCacheEntry
        ] = {}

        self._request_lock = asyncio.Lock()

        self._last_request_time = 0.0

    async def buscar(
        self,
        consulta: str,
        limite: int = 5,
    ) -> list[LocationResult]:

        consulta = consulta.strip()

        if not consulta:
            raise ValueError(
                "Localização não informada."
            )

        limite = max(
            1,
            min(int(limite), 5)
        )

        chave = consulta.casefold()

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
            return cache.resultados[:limite]

        async with self._request_lock:

            cache = self._cache.get(
                chave
            )

            agora = datetime.now(
                timezone.utc
            )

            if (
                cache
                and cache.expires_at > agora
            ):
                return cache.resultados[:limite]

            await self._respeitar_limite()

            params = {
                "q": consulta,
                "format": "jsonv2",
                "addressdetails": 1,
                "limit": limite,
                "accept-language": "pt-BR",
            }

            headers = {
                "User-Agent":
                    self.USER_AGENT,

                "Accept":
                    "application/json",
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

                self._last_request_time = (
                    time.monotonic()
                )

            except httpx.RequestError as erro:

                raise GeocodingProviderError(
                    "Não foi possível conectar "
                    "ao serviço de localização."
                ) from erro

        if response.status_code == 429:

            raise GeocodingProviderError(
                "O serviço de localização "
                "limitou temporariamente "
                "as requisições."
            )

        if response.status_code >= 400:

            raise GeocodingProviderError(
                "Erro no serviço de localização "
                f"(HTTP {response.status_code})."
            )

        try:

            dados = response.json()

        except ValueError as erro:

            raise GeocodingProviderError(
                "Resposta inválida do serviço "
                "de localização."
            ) from erro

        resultados = []

        for item in dados:

            endereco = (
                item.get("address")
                or {}
            )

            numero_endereco = (
                endereco.get(
                    "house_number"
                )
            )

            if (
                numero_endereco
                and nome.strip()
                == str(
                    numero_endereco
                ).strip()
            ):
                continue

            cidade = (
                endereco.get("city")
                or endereco.get("town")
                or endereco.get("village")
                or endereco.get("municipality")
            )

            estado = endereco.get(
                "state"
            )

            pais = endereco.get(
                "country"
            )

            codigo_pais = endereco.get(
                "country_code"
            )

            nome = (
                item.get("name")
                or cidade
                or consulta
            )

            try:

                latitude = float(
                    item["lat"]
                )

                longitude = float(
                    item["lon"]
                )

            except (
                KeyError,
                TypeError,
                ValueError,
            ):
                continue

            resultados.append(
                LocationResult(
                    nome=nome,

                    nome_completo=(
                        item.get(
                            "display_name"
                        )
                        or nome
                    ),

                    latitude=latitude,
                    longitude=longitude,

                    cidade=cidade,
                    estado=estado,
                    pais=pais,

                    codigo_pais=(
                        codigo_pais.upper()
                        if codigo_pais
                        else None
                    ),

                    provider=(
                        "Nominatim / OpenStreetMap"
                    ),
                )
            )

        self._cache[chave] = (
            _GeocodingCacheEntry(
                resultados=resultados,

                expires_at=(
                    datetime.now(
                        timezone.utc
                    )
                    + self.CACHE_DURATION
                ),
            )
        )

        return resultados[:limite]


    async def _buscar_nominatim_generico(
        self,
        latitude: float,
        longitude: float,
        raio_m: int,
        limite: int
    ) -> list[dict[str, Any]]:

        categorias = [
            "restaurante",
            "farmacia",
            "supermercado",
            "cafe"
        ]

        encontrados = []

        for indice, categoria in enumerate(
            categorias
        ):

            if indice > 0:
                await asyncio.sleep(
                    1.1
                )

            try:

                resultado = (
                    await self._buscar_nominatim(
                        latitude=latitude,
                        longitude=longitude,
                        categoria=categoria,
                        raio_m=raio_m,
                        limite=4
                    )
                )

                encontrados.extend(
                    resultado
                )

            except (
                httpx.HTTPError,
                TimeoutError
            ) as erro:

                print(
                    "[NEARBY] Nominatim "
                    f"falhou em {categoria}: "
                    f"{erro!r}"
                )

                continue

        # -------------------------------------------------
        # REMOVE DUPLICADOS
        # -------------------------------------------------

        unicos = {}

        for lugar in encontrados:

            osm_tipo = lugar.get(
                "osm_tipo"
            )

            osm_id = lugar.get(
                "osm_id"
            )

            if (
                osm_tipo
                and osm_id
            ):
                chave = (
                    osm_tipo,
                    osm_id
                )

            else:
                chave = (
                    lugar.get(
                        "nome"
                    ),
                    lugar.get(
                        "latitude"
                    ),
                    lugar.get(
                        "longitude"
                    )
                )

            unicos[chave] = lugar

        lugares = list(
            unicos.values()
        )

        lugares.sort(
            key=lambda lugar:
                lugar.get(
                    "distancia_m",
                    float("inf")
                )
        )

        return lugares[:limite]

    async def _respeitar_limite(
        self
    ) -> None:

        agora = time.monotonic()

        decorrido = (
            agora
            - self._last_request_time
        )

        restante = (
            self.MIN_REQUEST_INTERVAL
            - decorrido
        )

        if restante > 0:
            await asyncio.sleep(
                restante
            )