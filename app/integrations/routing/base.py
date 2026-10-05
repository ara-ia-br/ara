from abc import ABC, abstractmethod
from typing import Any


class RoutingProvider(ABC):

    @abstractmethod
    def calcular_rota(
            self,
            origem_lat: float,
            origem_log: float,
            destino_lat: float,
            destino_lon: float
    ) -> dict[str, Any]:
        """
        Calcula uma rota entre dois pontos geográficos.

        Deve retornar:
        - distancia_m
        - duraao_s
        - geometria GeoJSON
        """

        raise NotImplementedError