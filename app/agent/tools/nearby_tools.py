from __future__ import annotations

import httpx

from sqlalchemy.orm import Session

from app.integrations.async_runtime import (
    AsyncIntegrationRuntime
)

from app.services.nearby_service import (
    NearbyService
)


_nearby_service = NearbyService()


async def _consultar_lugares_proximos_async(
    latitude: float,
    longitude: float,
    categoria: str | None = None,
    raio_m: int = 1500,
    accuracy: float | None = None
) -> dict:

    lugares = await _nearby_service.buscar(
        latitude=latitude,
        longitude=longitude,
        categoria=categoria,
        raio_m=raio_m,
        limite=10
    )


    return {
        "sucesso":
            True,

        "tipo":
            "lugares_proximos",

        "somente_leitura":
            True,

        "categoria":
            categoria,

        "raio_m":
            raio_m,

        "accuracy_m":
            accuracy,

        "origem": {
            "latitude":
                float(latitude),

            "longitude":
                float(longitude)
        },

        "lugares":
            lugares,

        "provider":
            "Overpass / OpenStreetMap"
    }


def consultar_lugares_proximos(
    latitude: float | None = None,
    longitude: float | None = None,
    categoria: str | None = None,
    raio_m: int = 1500,
    accuracy: float | None = None,
    db: Session | None = None,
    id_usuario: int | None = None
) -> dict:

    if (
        latitude is None
        or longitude is None
    ):

        return {
            "sucesso":
                False,

            "tipo":
                "lugares_proximos",

            "somente_leitura":
                True,

            "erro":
                (
                    "Ative sua localização para "
                    "eu procurar lugares perto de você."
                )
        }


    try:

        return (
            AsyncIntegrationRuntime
            .executar(
                _consultar_lugares_proximos_async(
                    latitude=latitude,
                    longitude=longitude,
                    categoria=categoria,
                    raio_m=raio_m,
                    accuracy=accuracy
                )
            )
        )


    except (
        ValueError,
        httpx.HTTPError,
        TimeoutError,
        RuntimeError
    ) as erro:

        return {
            "sucesso":
                False,

            "tipo":
                "lugares_proximos",

            "somente_leitura":
                True,

            "erro":
                str(erro)
        }


    except Exception as erro:

        print(
            "[NEARBY TOOL] Erro inesperado:",
            repr(erro)
        )

        return {
            "sucesso":
                False,

            "tipo":
                "lugares_proximos",

            "somente_leitura":
                True,

            "erro":
                (
                    "Não consegui procurar "
                    "lugares próximos agora."
                )
        }

