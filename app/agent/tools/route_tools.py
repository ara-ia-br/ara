from __future__ import annotations

from sqlalchemy.orm import Session

from app.integrations.async_runtime import (
    AsyncIntegrationRuntime
)

from app.services.route_service import (
    RouteService
)


_route_service = RouteService()


# =========================================================
# CONSULTA ASSÍNCRONA
# =========================================================

async def _consultar_rota_async(
    origem: str,
    destino: str,
    origem_latitude: float | None = None,
    origem_longitude: float | None = None
) -> dict:

    origem = str(
        origem or ""
    ).strip()

    destino = str(
        destino or ""
    ).strip()


    if not origem:
        raise ValueError(
            "Informe a origem da rota."
        )

    if not destino:
        raise ValueError(
            "Informe o destino da rota."
        )


    # -----------------------------------------------------
    # CALCULA ROTA
    # -----------------------------------------------------

    rota = await _route_service.calcular(
        origem=origem,
        destino=destino,
        origem_latitude=origem_latitude,
        origem_longitude=origem_longitude
    )


    # -----------------------------------------------------
    # VISUALIZAÇÃO NATIVA
    # -----------------------------------------------------

    visualizacao = {
        "tipo": "rota",
        "versao": 1,

        "origem":
            rota.get("origem"),

        "destino":
            rota.get("destino"),

        "distancia_m":
            rota.get("distancia_m"),

        "distancia_km":
            rota.get("distancia_km"),

        "duracao_s":
            rota.get("duracao_s"),

        "duracao_min":
            rota.get("duracao_min"),

        "geometria":
            rota.get("geometria"),

        "fonte":
            "OSRM / OpenStreetMap",

        "atribuicao":
            "Dados de mapa © OpenStreetMap contributors"
    }


    return {
        "sucesso": True,

        "tipo": "rota",

        "rota":
            rota,

        "visualizacao":
            visualizacao,

        "somente_leitura": True
    }


# =========================================================
# TOOL SÍNCRONA
# =========================================================

def consultar_rota(
            origem: str,
            destino: str,
            origem_latitude: float | None = None,
            origem_longitude: float | None = None,
            db: Session | None = None,
            id_usuario: int | None = None
    ) -> dict:

    try:

        return (
            AsyncIntegrationRuntime
            .executar(
                _consultar_rota_async(
                    origem=origem,
                    destino=destino,
                    origem_latitude=origem_latitude,
                    origem_longitude=origem_longitude
                ),
                timeout=30.0
            )
        )

    except (
        ValueError,
        TimeoutError
    ) as erro:

        return {
            "sucesso": False,
            "erro": str(erro),
            "tipo": "rota",
            "somente_leitura": True
        }

    except Exception as erro:

        print(
            "[ROUTE TOOL] "
            "Erro inesperado:",
            repr(erro)
        )

        return {
            "sucesso": False,
            "erro": (
                "Não consegui calcular "
                "essa rota neste momento."
            ),
            "tipo": "rota",
            "somente_leitura": True
        }

