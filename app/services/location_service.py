from __future__ import annotations

import re
import unicodedata
from difflib import SequenceMatcher
from dataclasses import asdict, is_dataclass

from app.integrations.geocoding.nominatim_provider import (
    NominatimGeocodingProvider
)


class LocationService:

    def __init__(
        self,
        provider=None
    ):
        self.provider = (
            provider
            or NominatimGeocodingProvider()
        )


    # =========================================================
    # NORMALIZAÇÃO
    # =========================================================

    @staticmethod
    def _normalizar(
        valor: str | None
    ) -> str:

        texto = str(
            valor or ""
        ).strip().lower()

        texto = unicodedata.normalize(
            "NFD",
            texto
        )

        texto = "".join(
            caractere
            for caractere in texto
            if unicodedata.category(
                caractere
            ) != "Mn"
        )

        texto = re.sub(
            r"\s+",
            " ",
            texto
        )

        return texto.strip()


    # =========================================================
    # CANDIDATOS DE NOME
    # =========================================================

    @classmethod
    def _nomes_resultado(
        cls,
        resultado: dict
    ) -> list[str]:

        valores = [
            resultado.get("nome"),
            resultado.get("cidade"),
            resultado.get("municipio"),
            resultado.get("town"),
            resultado.get("village"),
        ]

        nome_completo = resultado.get(
            "nome_completo"
        )

        if nome_completo:

            valores.append(
                nome_completo
                .split(",")[0]
                .strip()
            )

        normalizados = []

        for valor in valores:

            valor_normalizado = (
                cls._normalizar(
                    valor
                )
            )

            if (
                valor_normalizado
                and valor_normalizado
                not in normalizados
            ):
                normalizados.append(
                    valor_normalizado
                )

        return normalizados


    # =========================================================
    # SCORE
    # =========================================================

    @classmethod
    def _pontuar(
        cls,
        consulta: str,
        resultado: dict
    ) -> float:

        consulta_normalizada = (
            cls._normalizar(
                consulta
            )
        )

        if not consulta_normalizada:
            return 0

        nomes = cls._nomes_resultado(
            resultado
        )

        score = 0.0


        # -----------------------------------------------------
        # MATCH EXATO
        # -----------------------------------------------------

        if consulta_normalizada in nomes:
            score += 100


        # -----------------------------------------------------
        # SEMELHANÇA
        # -----------------------------------------------------

        melhor_similaridade = 0.0

        for nome in nomes:

            similaridade = (
                SequenceMatcher(
                    None,
                    consulta_normalizada,
                    nome
                )
                .ratio()
            )

            melhor_similaridade = max(
                melhor_similaridade,
                similaridade
            )

        score += (
            melhor_similaridade
            * 40
        )


        # -----------------------------------------------------
        # NOME COMPLETO
        # -----------------------------------------------------

        nome_completo = (
            cls._normalizar(
                resultado.get(
                    "nome_completo"
                )
            )
        )

        if (
            consulta_normalizada
            and consulta_normalizada
            in nome_completo
        ):
            score += 20


        # -----------------------------------------------------
        # BRASIL
        # -----------------------------------------------------

        pais = cls._normalizar(
            resultado.get("pais")
        )

        if pais in {
            "brasil",
            "brazil"
        }:
            score += 10


        # -----------------------------------------------------
        # TIPO DE LOCAL
        # -----------------------------------------------------

        tipo = cls._normalizar(
            resultado.get("tipo")
        )

        if tipo in {
            "city",
            "town",
            "municipality",
            "municipio",
            "cidade"
        }:
            score += 15


        return score


    # =========================================================
    # BUSCA BRUTA
    # =========================================================

    async def buscar(
        self,
        consulta: str,
        limite: int = 5
    ) -> list[dict]:

        resultados = await self.provider.buscar(
            consulta=consulta,
            limite=limite
        )

        convertidos: list[dict] = []

        for resultado in resultados:

            # Provider pode devolver dict
            if isinstance(
                resultado,
                dict
            ):
                convertidos.append(
                    resultado.copy()
                )
                continue

            # LocationResult é dataclass
            if is_dataclass(
                resultado
            ):
                convertidos.append(
                    asdict(resultado)
                )
                continue

            # Fallback para objeto comum
            if hasattr(
                resultado,
                "__dict__"
            ):
                convertidos.append(
                    vars(resultado).copy()
                )
                continue

        return convertidos


    # =========================================================
    # RESOLVER LOCAL
    # =========================================================

    async def resolver(
        self,
        consulta: str,
        limite: int = 8
    ) -> dict | None:

        consulta = str(
            consulta or ""
        ).strip()

        if not consulta:
            return None

        resultados = (
            await self.buscar(
                consulta=consulta,
                limite=max(
                    limite,
                    5
                )
            )
        )

        if not resultados:
            return None


        ranqueados = sorted(
            resultados,
            key=lambda resultado:
                self._pontuar(
                    consulta,
                    resultado
                ),
            reverse=True
        )


        melhor = ranqueados[0]

        melhor_score = (
            self._pontuar(
                consulta,
                melhor
            )
        )


        # Consulta muito curta como RJ/SP:
        # mantém o melhor resultado do geocoder.
        consulta_normalizada = (
            self._normalizar(
                consulta
            )
        )

        if len(
            consulta_normalizada
        ) <= 3:
            return melhor


        # Não aceita uma cidade completamente
        # diferente só porque foi o primeiro
        # resultado do Nominatim.
        if melhor_score < 60:
            return None


        return melhor