from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)

from app.integrations.geocoding.base import (
    GeocodingProviderError,
)
from app.integrations.weather.base import (
    WeatherProviderError,
)
from app.security.depedencies import (
    obter_usuario_atual,
)
from app.services.location_service import (
    LocationService,
)
from app.services.weather_service import (
    WeatherService,
)


router = APIRouter(
    prefix="/integracoes/clima",
    tags=["Integrações - Clima"],
)


# ============================================================
# SERVICES
# ============================================================

weather_service = WeatherService()

location_service = LocationService()


# ============================================================
# CLIMA ATUAL POR COORDENADAS
# ============================================================

@router.get("/atual")
async def obter_clima_atual(
    latitude: float = Query(
        ...,
        ge=-90,
        le=90,
        description="Latitude da localização.",
    ),
    longitude: float = Query(
        ...,
        ge=-180,
        le=180,
        description="Longitude da localização.",
    ),
    usuario_atual=Depends(
        obter_usuario_atual
    ),
):
    try:

        clima = (
            await weather_service
            .obter_clima_atual(
                latitude=latitude,
                longitude=longitude,
            )
        )

        return {
            "sucesso": True,
            "clima": clima,
        }

    except WeatherProviderError as erro:

        raise HTTPException(
            status_code=(
                status.HTTP_503_SERVICE_UNAVAILABLE
            ),
            detail=str(erro),
        ) from erro

    except ValueError as erro:

        raise HTTPException(
            status_code=(
                status.HTTP_400_BAD_REQUEST
            ),
            detail=str(erro),
        ) from erro

    except Exception as erro:

        print(
            "[WEATHER] Erro inesperado:",
            repr(erro),
        )

        raise HTTPException(
            status_code=(
                status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail=(
                "Erro interno ao consultar "
                "informações meteorológicas."
            ),
        ) from erro


# ============================================================
# CLIMA ATUAL POR NOME DO LOCAL
# ============================================================

@router.get("/local")
async def obter_clima_por_local(
    local: str = Query(
        ...,
        min_length=2,
        max_length=150,
        description=(
            "Cidade, município ou localização."
        ),
    ),
    usuario_atual=Depends(
        obter_usuario_atual
    ),
):
    try:

        locais = (
            await location_service.buscar(
                consulta=local,
                limite=3,
            )
        )

        if not locais:

            raise HTTPException(
                status_code=(
                    status.HTTP_404_NOT_FOUND
                ),
                detail=(
                    "Localização não encontrada."
                ),
            )

        local_encontrado = locais[0]

        clima = (
            await weather_service
            .obter_clima_atual(
                latitude=(
                    local_encontrado[
                        "latitude"
                    ]
                ),
                longitude=(
                    local_encontrado[
                        "longitude"
                    ]
                ),
            )
        )

        return {
            "sucesso": True,

            "local": {
                "consulta":
                    local,

                "nome":
                    local_encontrado[
                        "nome"
                    ],

                "nome_completo":
                    local_encontrado[
                        "nome_completo"
                    ],

                "cidade":
                    local_encontrado[
                        "cidade"
                    ],

                "estado":
                    local_encontrado[
                        "estado"
                    ],

                "pais":
                    local_encontrado[
                        "pais"
                    ],

                "codigo_pais":
                    local_encontrado[
                        "codigo_pais"
                    ],

                "latitude":
                    local_encontrado[
                        "latitude"
                    ],

                "longitude":
                    local_encontrado[
                        "longitude"
                    ],

                "fonte":
                    local_encontrado[
                        "fonte"
                    ],
            },

            "clima": clima,
        }

    except HTTPException:
        raise

    except GeocodingProviderError as erro:

        raise HTTPException(
            status_code=(
                status.HTTP_503_SERVICE_UNAVAILABLE
            ),
            detail=str(erro),
        ) from erro

    except WeatherProviderError as erro:

        raise HTTPException(
            status_code=(
                status.HTTP_503_SERVICE_UNAVAILABLE
            ),
            detail=str(erro),
        ) from erro

    except ValueError as erro:

        raise HTTPException(
            status_code=(
                status.HTTP_400_BAD_REQUEST
            ),
            detail=str(erro),
        ) from erro

    except Exception as erro:

        print(
            "[WEATHER] Erro inesperado:",
            repr(erro),
        )

        raise HTTPException(
            status_code=(
                status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail=(
                "Erro interno ao consultar "
                "o clima da localização."
            ),
        ) from erro