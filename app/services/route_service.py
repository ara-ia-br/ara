from __future__ import annotations

import asyncio
from typing import Any

from app.integrations.routing.osrm_provider import (
    OSRMRoutingProvider
)

from app.services.location_service import (
    LocationService
)


class RouteService:

    def __init__(
        self,
        location_service: LocationService | None = None,
        routing_provider=None
    ):
        self.location_service = (
            location_service
            or LocationService()
        )

        self.routing_provider = (
            routing_provider
            or OSRMRoutingProvider()
        )


    # =========================================================
    # COORDENADAS
    # =========================================================

    @staticmethod
    def _coordenadas(
        local: dict
    ) -> tuple[float, float]:

        latitude = (
            local.get("latitude")
            if local.get("latitude") is not None
            else local.get("lat")
        )

        longitude = (
            local.get("longitude")
            if local.get("longitude") is not None
            else local.get("lon")
        )

        if (
            latitude is None
            or longitude is None
        ):
            raise ValueError(
                "O local encontrado não possui "
                "coordenadas válidas."
            )

        return (
            float(latitude),
            float(longitude)
        )


    # =========================================================
    # NOME DO LOCAL
    # =========================================================

    @staticmethod
    def _nome_local(
        local: dict,
        fallback: str
    ) -> str:

        return str(
            local.get("nome_completo")
            or local.get("nome")
            or local.get("cidade")
            or fallback
        ).strip()


    # =========================================================
    # CALCULAR ROTA
    # =========================================================

    async def calcular(
        self,
        origem: str,
        destino: str,
        origem_latitude: float | None = None,
        origem_longitude: float | None = None
    ) -> dict[str, Any]:

        origem = str(
            origem or ""
        ).strip()

        destino = str(
            destino or ""
        ).strip()


        if not origem:
            raise ValueError(
                "A origem da rota não foi informada."
            )

        if not destino:
            raise ValueError(
                "O destino da rota não foi informado."
            )


        # =====================================================
        # ORIGEM
        # =====================================================

        usa_origem_gps = (
            origem_latitude is not None
            or origem_longitude is not None
        )


        if usa_origem_gps:

            if (
                origem_latitude is None
                or origem_longitude is None
            ):
                raise ValueError(
                    "As coordenadas da localização atual "
                    "estão incompletas."
                )


            origem_lat = float(
                origem_latitude
            )

            origem_lon = float(
                origem_longitude
            )


            if not -90 <= origem_lat <= 90:
                raise ValueError(
                    "Latitude da localização atual inválida."
                )

            if not -180 <= origem_lon <= 180:
                raise ValueError(
                    "Longitude da localização atual inválida."
                )


            local_origem = {
                "nome":
                    "Sua localização atual",

                "nome_completo":
                    "Sua localização atual",

                "latitude":
                    origem_lat,

                "longitude":
                    origem_lon
            }


            local_destino = (
                await self.location_service.resolver_local(
                    destino
                )
            )


        else:

            local_origem, local_destino = (
                await asyncio.gather(

                    self.location_service.resolver_local(
                        origem
                    ),

                    self.location_service.resolver_local(
                        destino
                    )
                )
            )


            if local_origem is None:
                raise ValueError(
                    f"Não consegui localizar a origem: "
                    f"{origem}."
                )


        if local_destino is None:
            raise ValueError(
                f"Não consegui localizar o destino: "
                f"{destino}."
            )


        # =====================================================
        # COORDENADAS
        # =====================================================

        origem_lat, origem_lon = (
            self._coordenadas(
                local_origem
            )
        )

        destino_lat, destino_lon = (
            self._coordenadas(
                local_destino
            )
        )


        # =====================================================
        # ROUTING
        # =====================================================

        rota = await asyncio.to_thread(
            self.routing_provider.calcular_rota,
            origem_lat,
            origem_lon,
            destino_lat,
            destino_lon
        )


        distancia_m = float(
            rota.get("distancia_m")
            or 0
        )

        duracao_s = float(
            rota.get("duracao_s")
            or 0
        )


        # =====================================================
        # RESULTADO
        # =====================================================

        return {
            "origem": {
                "consulta":
                    origem,

                "nome":
                    self._nome_local(
                        local_origem,
                        origem
                    ),

                "latitude":
                    origem_lat,

                "longitude":
                    origem_lon
            },

            "destino": {
                "consulta":
                    destino,

                "nome":
                    self._nome_local(
                        local_destino,
                        destino
                    ),

                "latitude":
                    destino_lat,

                "longitude":
                    destino_lon
            },

            "distancia_m":
                distancia_m,

            "distancia_km":
                round(
                    distancia_m / 1000,
                    1
                ),

            "duracao_s":
                duracao_s,

            "duracao_min":
                round(
                    duracao_s / 60
                ),

            "geometria":
                rota.get(
                    "geometria"
                ),

            "considera_transito":
                False,

            "provider":
                "OSRM / OpenStreetMap"
        }