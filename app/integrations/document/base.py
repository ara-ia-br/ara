from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path


class DocumentExtractor(ABC):

    @abstractmethod
    def extrair(
            self,
            caminho: Path
    ) -> str:
        raise NotImplementedError