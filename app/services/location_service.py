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
    # NORMALIZAÇÃO DE CONSULTA GEOGRÁFICA
    # =========================================================

    @classmethod
    def _normalizar_consulta_geografica(
            cls,
            consulta: str
    ) -> str:

        consulta = str(
            consulta or ""
        ).strip()

        if not consulta:
            return consulta

        texto = (
            cls._normalizar(
                consulta
            )
            .replace(",", " ")
        )

        texto = re.sub(
            r"\s+",
            " ",
            texto
        ).strip()

        # -----------------------------------------------------
        # CENTRO DO RIO
        # -----------------------------------------------------
        #
        # Exemplos:
        #
        # Centro do Rio
        # Centro do Rio de Janeiro
        # Centro do Rio de Janeiro, RJ
        # Centro de Rio de Janeiro
        #
        # -----------------------------------------------------

        if re.fullmatch(
                (
                        r"centro\s+"
                        r"(?:do|de)\s+"
                        r"rio"
                        r"(?:\s+de\s+janeiro)?"
                        r"(?:\s+rj)?"
                ),
                texto,
                flags=re.IGNORECASE
        ):
            return (
                "Centro, Rio de Janeiro, "
                "RJ, Brasil"
            )

        return consulta



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

    async def resolver_local(
            self,
            consulta: str,
            limite: int = 8
    ) -> dict | None:

        consulta = str(
            consulta or ""
        ).strip()

        if not consulta:
            return None

            # =====================================================
            # NORMALIZA CONSULTA GEOGRÁFICA
            # =====================================================

        consulta = (
            self._normalizar_consulta_geografica(
                consulta
            )
        )

        resultados = await self.buscar(
            consulta=consulta,
            limite=max(
                limite,
                5
            )
        )

        if not resultados:
            return None

        consulta_normalizada = (
            self._normalizar(
                consulta
            )
        )

        partes_consulta = [
            self._normalizar(
                parte
            )
            for parte in consulta.split(",")
            if self._normalizar(
                parte
            )
        ]

        def pontuar_local(
                resultado: dict
        ) -> float:

            score = 0.0

            nome = self._normalizar(
                resultado.get("nome")
            )

            cidade = self._normalizar(
                resultado.get("cidade")
            )

            estado = self._normalizar(
                resultado.get("estado")
            )

            nome_completo = self._normalizar(
                resultado.get(
                    "nome_completo"
                )
            )

            # -------------------------------------------------
            # PRIMEIRA PARTE DA CONSULTA
            # -------------------------------------------------

            if partes_consulta:

                principal = (
                    partes_consulta[0]
                )

                if nome == principal:
                    score += 100

                elif principal in nome_completo:
                    score += 60

            # -------------------------------------------------
            # DEMAIS PARTES
            # -------------------------------------------------

            for parte in partes_consulta[1:]:

                if parte == cidade:
                    score += 60

                elif parte == estado:
                    score += 40

                elif parte in nome_completo:
                    score += 25

            # -------------------------------------------------
            # CONSULTA COMPLETA
            # -------------------------------------------------

            if (
                    consulta_normalizada
                    in nome_completo
            ):
                score += 50

            # -------------------------------------------------
            # BRASIL
            # -------------------------------------------------

            pais = self._normalizar(
                resultado.get("pais")
            )

            if pais in {
                "brasil",
                "brazil"
            }:
                score += 10

            return score

        ranqueados = sorted(
            resultados,
            key=pontuar_local,
            reverse=True
        )

        melhor = ranqueados[0]

        melhor_score = (
            pontuar_local(
                melhor
            )
        )

        if melhor_score <= 0:
            return None

        return melhor