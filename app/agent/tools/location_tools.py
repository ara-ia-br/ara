from __future__ import annotations

from sqlalchemy.orm import Session

from app.integrations.async_runtime import (
    AsyncIntegrationRuntime
)

from app.services.current_location_service import (
    CurrentLocationService
)


_location_service = (
    CurrentLocationService()
)


# =========================================================
# ASSÍNCRONO
# =========================================================

async def _consultar_localizacao_atual_async(
    latitude: float,
    longitude: float,
    accuracy: float | None = None
) -> dict:

    local = await _location_service.resolver(
        latitude=latitude,
        longitude=longitude
    )


    return {
        "sucesso":
            True,

        "tipo":
            "localizacao_atual",

        "somente_leitura":
            True,

        "local":
            local,

        "accuracy_m":
            (
                float(accuracy)
                if accuracy is not None
                else None
            )
    }


# =========================================================
# TOOL SÍNCRONA
# =========================================================

def consultar_localizacao_atual(
    latitude: float | None = None,
    longitude: float | None = None,
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
                "localizacao_atual",

            "somente_leitura":
                True,

            "erro":
                (
                    "Ative sua localização para "
                    "eu conseguir identificar "
                    "onde você está."
                )
        }


    try:

        return (
            AsyncIntegrationRuntime
            .executar(
                _consultar_localizacao_atual_async(
                    latitude=latitude,
                    longitude=longitude,
                    accuracy=accuracy
                )
            )
        )


    except (
        ValueError,
        httpx.HTTPError,
        TimeoutError
    ) as erro:

        return {
            "sucesso":
                False,

            "tipo":
                "localizacao_atual",

            "somente_leitura":
                True,

            "erro":
                str(erro)
        }


    except Exception as erro:

        print(
            "[LOCATION TOOL] "
            "Erro inesperado:",
            repr(erro)
        )


        return {
            "sucesso":
                False,

            "tipo":
                "localizacao_atual",

            "somente_leitura":
                True,

            "erro":
                (
                    "Não consegui identificar "
                    "sua localização agora."
                )
        }