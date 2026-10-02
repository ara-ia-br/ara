from __future__ import annotations

from sqlalchemy.orm import Session

from app.integrations.async_runtime import (
    AsyncIntegrationRuntime
)
from app.integrations.geocoding.base import (
    GeocodingProviderError
)
from app.integrations.weather.base import (
    WeatherProviderError
)
from app.services.location_service import (
    LocationService
)
from app.services.weather_service import (
    WeatherService
)


_location_service = LocationService()
_weather_service = WeatherService()


# =========================================================
# CONSULTA ASSÍNCRONA
# =========================================================

async def _consultar_clima_local_async(
    local: str
) -> dict:

    local = local.strip()

    if not local:
        raise ValueError(
            "Informe uma localização."
        )

    # -----------------------------------------------------
    # GEOCODING
    # -----------------------------------------------------

    locais = await _location_service.buscar(
        consulta=local,
        limite=3
    )

    if not locais:
        return {
            "sucesso": False,
            "erro":
                "Não encontrei essa localização.",
            "tipo": "clima",
            "somente_leitura": True
        }

    local_encontrado = locais[0]

    latitude = (
        local_encontrado["latitude"]
    )

    longitude = (
        local_encontrado["longitude"]
    )

    # -----------------------------------------------------
    # CLIMA + 12 HORAS
    # -----------------------------------------------------

    painel = (
        await _weather_service
        .obter_painel_clima(
            latitude=latitude,
            longitude=longitude,
            horas=12
        )
    )

    clima_atual = painel["atual"]
    previsao_horaria = painel["horas"]

    # -----------------------------------------------------
    # LOCAL NORMALIZADO
    # -----------------------------------------------------

    local_normalizado = {
        "consulta":
            local,

        "nome":
            local_encontrado.get(
                "nome"
            ),

        "nome_completo":
            local_encontrado.get(
                "nome_completo"
            ),

        "cidade":
            local_encontrado.get(
                "cidade"
            ),

        "estado":
            local_encontrado.get(
                "estado"
            ),

        "pais":
            local_encontrado.get(
                "pais"
            ),

        "latitude":
            latitude,

        "longitude":
            longitude
    }

    # -----------------------------------------------------
    # VISUALIZAÇÃO NATIVA
    # -----------------------------------------------------

    visualizacao = {
        "tipo": "clima",
        "versao": 1,

        "local":
            local_normalizado,

        "atual": {
            "temperatura_c":
                clima_atual.get(
                    "temperatura_c"
                ),

            "condicao":
                clima_atual.get(
                    "condicao"
                ),

            "condicao_codigo":
                clima_atual.get(
                    "condicao_codigo"
                ),

            "umidade_percentual":
                clima_atual.get(
                    "umidade_percentual"
                ),

            "vento_m_s":
                clima_atual.get(
                    "vento_m_s"
                ),

            "precipitacao_mm":
                clima_atual.get(
                    "precipitacao_proxima_hora_mm"
                )
        },

        "horas": [
            {
                "horario":
                    item.get(
                        "horario_previsao"
                    ),

                "temperatura_c":
                    item.get(
                        "temperatura_c"
                    ),

                "precipitacao_mm":
                    item.get(
                        "precipitacao_proxima_hora_mm"
                    ),

                "condicao":
                    item.get(
                        "condicao"
                    ),

                "condicao_codigo":
                    item.get(
                        "condicao_codigo"
                    )
            }
            for item
            in previsao_horaria
        ],

        "fonte":
            clima_atual.get(
                "fonte"
            ),

        "atribuicao":
            clima_atual.get(
                "atribuicao"
            )
    }

    return {
        "sucesso": True,

        "tipo": "clima",

        "local":
            local_normalizado,

        # Mantemos porque o ResponseComposer
        # atual já utiliza esse objeto.
        "clima":
            clima_atual,

        "visualizacao":
            visualizacao,

        "somente_leitura": True
    }


# =========================================================
# TOOL SÍNCRONA
# =========================================================

def consultar_clima_local(
    local: str,
    db: Session | None = None,
    id_usuario: int | None = None
) -> dict:

    try:

        return (
            AsyncIntegrationRuntime
            .executar(
                _consultar_clima_local_async(
                    local=local
                ),
                timeout=30.0
            )
        )

    except (
        GeocodingProviderError,
        WeatherProviderError,
        ValueError,
        TimeoutError
    ) as erro:

        return {
            "sucesso": False,
            "erro": str(erro),
            "tipo": "clima",
            "somente_leitura": True
        }

    except Exception as erro:

        print(
            "[WEATHER TOOL] "
            "Erro inesperado:",
            repr(erro)
        )

        return {
            "sucesso": False,
            "erro":
                "Não consegui consultar "
                "o clima neste momento.",
            "tipo": "clima",
            "somente_leitura": True
        }