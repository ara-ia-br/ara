from __future__ import annotations

from app.integrations.geocoding.base import (
    GeocodingProvider,
)
from app.integrations.geocoding.nominatim_provider import (
    NominatimGeocodingProvider,
)


class LocationService:

    def __init__(
        self,
        provider: GeocodingProvider | None = None,
    ):
        self.provider = (
            provider
            or NominatimGeocodingProvider()
        )

    async def buscar(
        self,
        consulta: str,
        limite: int = 5,
    ) -> list[dict]:

        resultados = (
            await self.provider.buscar(
                consulta=consulta,
                limite=limite,
            )
        )

        return [
            {
                "nome": local.nome,
                "nome_completo": local.nome_completo,
                "latitude": local.latitude,
                "longitude": local.longitude,
                "cidade": local.cidade,
                "estado": local.estado,
                "pais": local.pais,
                "codigo_pais": local.codigo_pais,
                "fonte": local.provider,
                "atribuicao": (
                    "Dados de localização "
                    "© OpenStreetMap contributors."
                ),
            }
            for local in resultados
        ]