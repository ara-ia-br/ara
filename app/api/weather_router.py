from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)

from app.integrations.weather.base import (
    WeatherProviderError,
)
from app.security.depedencies import (
    obter_usuario_atual,
)
from app.services.weather_service import (
    WeatherService,
)


router = APIRouter(
    prefix="/integracoes/clima",
    tags=["Integrações - Clima"],
)


# ============================================================
# SERVICE
# ============================================================
#
# Uma única instância permanece ativa durante a execução
# da aplicação.
#
# Isso é importante porque o WeatherService/Provider
# mantém o cache meteorológico em memória.
# ============================================================

weather_service = WeatherService()


# ============================================================
# CLIMA ATUAL
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
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(erro),
        ) from erro

    except ValueError as erro:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(erro),
        ) from erro

    except Exception as erro:

        print(
            "[WEATHER] Erro inesperado:",
            repr(erro),
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "Erro interno ao consultar "
                "informações meteorológicas."
            ),
        ) from erro