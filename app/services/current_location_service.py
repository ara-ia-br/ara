from __future__ import annotations

from typing import Any

import httpx


class CurrentLocationService:

    _URL = (
        "https://nominatim.openstreetmap.org/reverse"
    )

    _HEADERS = {
        "User-Agent":
            "ARA/1.0"
    }


    async def resolver(
        self,
        latitude: float,
        longitude: float
    ) -> dict[str, Any]:

        latitude = float(
            latitude
        )

        longitude = float(
            longitude
        )


        # =====================================================
        # VALIDAÇÃO
        # =====================================================

        if not (
            -90 <= latitude <= 90
        ):
            raise ValueError(
                "Latitude inválida."
            )


        if not (
            -180 <= longitude <= 180
        ):
            raise ValueError(
                "Longitude inválida."
            )


        # =====================================================
        # REVERSE GEOCODING
        # =====================================================

        parametros = {
            "format":
                "jsonv2",

            "lat":
                latitude,

            "lon":
                longitude,

            "zoom":
                18,

            "addressdetails":
                1,

            "accept-language":
                "pt-BR"
        }


        async with httpx.AsyncClient(
            timeout=15.0,
            headers=self._HEADERS
        ) as client:

            resposta = await client.get(
                self._URL,
                params=parametros
            )


        resposta.raise_for_status()


        dados = resposta.json()


        # =====================================================
        # VALIDA RESPOSTA
        # =====================================================

        if (
            not isinstance(
                dados,
                dict
            )
            or dados.get(
                "error"
            )
        ):

            raise ValueError(
                "Não consegui identificar "
                "essa localização."
            )


        endereco = (
            dados.get(
                "address"
            )
            or {}
        )


        # =====================================================
        # COMPONENTES DO ENDEREÇO
        # =====================================================

        bairro = (
            endereco.get(
                "neighbourhood"
            )
            or endereco.get(
                "suburb"
            )
            or endereco.get(
                "quarter"
            )
            or endereco.get(
                "city_district"
            )
            or endereco.get(
                "district"
            )
        )


        cidade = (
            endereco.get(
                "city"
            )
            or endereco.get(
                "town"
            )
            or endereco.get(
                "municipality"
            )
            or endereco.get(
                "village"
            )
        )


        estado = (
            endereco.get(
                "state"
            )
        )


        pais = (
            endereco.get(
                "country"
            )
        )


        logradouro = (
            endereco.get(
                "road"
            )
            or endereco.get(
                "pedestrian"
            )
            or endereco.get(
                "residential"
            )
            or endereco.get(
                "footway"
            )
        )


        numero = (
            endereco.get(
                "house_number"
            )
        )


        cep = (
            endereco.get(
                "postcode"
            )
        )


        # =====================================================
        # RETORNO
        # =====================================================

        return {
            "nome_completo":
                dados.get(
                    "display_name"
                ),

            "logradouro":
                logradouro,

            "numero":
                numero,

            "bairro":
                bairro,

            "cidade":
                cidade,

            "estado":
                estado,

            "pais":
                pais,

            "cep":
                cep,

            "latitude":
                latitude,

            "longitude":
                longitude,

            "provider":
                "Nominatim / OpenStreetMap"
        }