from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True, frozen=True)
class WeatherSnapshot:
    latitude: float
    longitude: float

    temperature_c: float | None
    humidity_percent: float | None

    wind_speed_mps: float | None
    wind_direction_deg: float | None

    air_pressure_hpa: float | None

    precipitation_next_hour_mm: float | None

    condition_code: str | None

    forecast_time: datetime

    provider: str


class WeatherProviderError(RuntimeError):
    pass

class WeatherProvider(ABC):

    @abstractmethod
    async def obter_clima_atual(
            self,
            latitude: float,
            longitude: float
    ) -> WeatherSnapshot:
        raise NotImplementedError