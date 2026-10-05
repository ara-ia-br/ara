from typing import Any

import httpx

from app.integrations.routing.base import (
    RoutingProvider
)

class OSRMRoutingProvider(
    RoutingProvider
):
    BASE_URL = (
        "https://router.project-osrm.org"
    )

    def calcular_rota(
            self,
            origem_lat: float,
            origem_log: float,
            destino_lat: float,
            destino_lon: float
    ) -> dict[str, Any]:

        coordenadas = (
            f"{origem_log},{origem_lat};"
            f"{destino_lon},{destino_lat}"
        )


        url = (
            f"{self.BASE_URL}"
            f"/route/v1/driving/"
            f"{coordenadas}"
        )

        parametros = {
            "overview": "full",
            "geometries": "geojson",
            "steps": "false"
        }

        resposta = httpx.get(
            url,
            params=parametros,
            timeout=20
        )

        resposta.raise_for_status()

        dados = resposta.json()

        rotas = dados.get(
            "routes",
            []
        )

        if not rotas:
            raise ValueError(
                "Nenhuam rota encontrada."
            )

        rota = rotas[0]

        return {
            "distancia_m": rota.get(
                "distance"
            ),

            "duracao_s": rota.get(
                "duration"
            ),

            "geometria": rota.get(
                "geometry"
            )
        }