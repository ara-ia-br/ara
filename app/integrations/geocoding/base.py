from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class LocationResult:
    nome: str
    nome_completo: str

    latitude: float
    longitude: float

    cidade: str | None
    estado: str | None
    pais: str | None
    codigo_pais: str | None

    provider: str

class GeocodingProviderError(RuntimeError):
    pass

class GeocodingProvider(ABC):

    @abstractmethod
    async def buscar(
            self,
            consulta: str,
            limite: int = 5,
    ) -> list[LocationResult]:
        raise NotImplementedError