from __future__ import annotations

from math import atan2, cos, radians, sin, sqrt
from typing import Any

import httpx


class NearbyService:

    _URL = (
        "https://overpass-api.de/api/interpreter"
    )

    _HEADERS = {
        "User-Agent":
            "ARA/1.0"
    }

    _FILTROS = {
        "restaurante": [
            '["amenity"="restaurant"]'
        ],

        "lanchonete": [
            '["amenity"="fast_food"]'
        ],

        "cafe": [
            '["amenity"="cafe"]'
        ],

        "bar": [
            '["amenity"="bar"]'
        ],

        "farmacia": [
            '["amenity"="pharmacy"]'
        ],

        "hospital": [
            '["amenity"="hospital"]'
        ],

        "mercado": [
            '["shop"~"supermarket|convenience|greengrocer"]'
        ],

        "supermercado": [
            '["shop"="supermarket"]'
        ],

        "posto": [
            '["amenity"="fuel"]'
        ],

        "banco": [
            '["amenity"="bank"]'
        ],

        "atm": [
            '["amenity"="atm"]'
        ],

        "academia": [
            '["leisure"="fitness_centre"]'
        ],

        "parque": [
            '["leisure"="park"]'
        ],

        "hotel": [
            '["tourism"="hotel"]'
        ],

        "estacionamento": [
            '["amenity"="parking"]'
        ]
    }


    @staticmethod
    def _distancia_metros(
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float
    ) -> float:

        raio = 6371000

        phi1 = radians(lat1)
        phi2 = radians(lat2)

        delta_phi = radians(
            lat2 - lat1
        )

        delta_lambda = radians(
            lon2 - lon1
        )

        a = (
            sin(delta_phi / 2) ** 2
            + cos(phi1)
            * cos(phi2)
            * sin(delta_lambda / 2) ** 2
        )

        c = (
            2
            * atan2(
                sqrt(a),
                sqrt(1 - a)
            )
        )

        return raio * c


    @staticmethod
    def _categoria_elemento(
        tags: dict[str, Any]
    ) -> str:

        amenity = tags.get(
            "amenity"
        )

        shop = tags.get(
            "shop"
        )

        leisure = tags.get(
            "leisure"
        )

        tourism = tags.get(
            "tourism"
        )

        mapa = {
            "restaurant": "Restaurante",
            "fast_food": "Lanchonete",
            "cafe": "Café",
            "bar": "Bar",
            "pharmacy": "Farmácia",
            "hospital": "Hospital",
            "bank": "Banco",
            "atm": "Caixa eletrônico",
            "fuel": "Posto",
            "parking": "Estacionamento",

            "supermarket": "Supermercado",
            "convenience": "Mercado",
            "greengrocer": "Hortifruti",

            "fitness_centre": "Academia",
            "park": "Parque",

            "hotel": "Hotel"
        }

        chave = (
            amenity
            or shop
            or leisure
            or tourism
        )

        return mapa.get(
            chave,
            "Local"
        )


    def _montar_filtros(
        self,
        categoria: str | None
    ) -> list[str]:

        if categoria:

            normalizada = (
                categoria
                .lower()
                .strip()
            )

            filtros = (
                self._FILTROS.get(
                    normalizada
                )
            )

            if filtros:
                return filtros


        return [
            (
                '["amenity"~'
                '"restaurant|fast_food|cafe|bar|'
                'pharmacy|hospital|bank|atm|fuel"]'
            ),
            (
                '["shop"~'
                '"supermarket|convenience|greengrocer|bakery"]'
            ),
            (
                '["leisure"~'
                '"fitness_centre|park"]'
            ),
            (
                '["tourism"~'
                '"hotel|museum|attraction"]'
            )
        ]


    async def buscar(
        self,
        latitude: float,
        longitude: float,
        categoria: str | None = None,
        raio_m: int = 1500,
        limite: int = 10
    ) -> list[dict[str, Any]]:

        latitude = float(
            latitude
        )

        longitude = float(
            longitude
        )


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


        raio_m = max(
            100,
            min(
                int(raio_m),
                5000
            )
        )


        filtros = (
            self._montar_filtros(
                categoria
            )
        )


        consultas = []


        for filtro in filtros:

            for tipo in (
                "node",
                "way",
                "relation"
            ):

                consultas.append(
                    (
                        f'{tipo}'
                        f'{filtro}'
                        f'(around:{raio_m},'
                        f'{latitude},'
                        f'{longitude});'
                    )
                )


        query = (
            "[out:json]"
            "[timeout:20];"
            "("
            + "".join(
                consultas
            )
            + ");"
            "out center tags;"
        )


        async with httpx.AsyncClient(
            timeout=25.0,
            headers=self._HEADERS
        ) as client:

            resposta = await client.post(
                self._URL,
                data={
                    "data":
                        query
                }
            )


        resposta.raise_for_status()

        dados = resposta.json()


        elementos = (
            dados.get(
                "elements"
            )
            or []
        )


        lugares = []

        chaves = set()


        for elemento in elementos:

            tags = (
                elemento.get(
                    "tags"
                )
                or {}
            )

            nome = tags.get(
                "name"
            )

            if not nome:
                continue


            if (
                elemento.get("type")
                == "node"
            ):

                lat = elemento.get(
                    "lat"
                )

                lon = elemento.get(
                    "lon"
                )

            else:

                centro = (
                    elemento.get(
                        "center"
                    )
                    or {}
                )

                lat = centro.get(
                    "lat"
                )

                lon = centro.get(
                    "lon"
                )


            if (
                lat is None
                or lon is None
            ):
                continue


            lat = float(lat)
            lon = float(lon)


            distancia = (
                self._distancia_metros(
                    latitude,
                    longitude,
                    lat,
                    lon
                )
            )


            chave = (
                nome.lower(),
                round(lat, 5),
                round(lon, 5)
            )


            if chave in chaves:
                continue


            chaves.add(
                chave
            )


            lugares.append({
                "nome":
                    nome,

                "categoria":
                    self._categoria_elemento(
                        tags
                    ),

                "latitude":
                    lat,

                "longitude":
                    lon,

                "distancia_m":
                    round(
                        distancia
                    ),

                "endereco":
                    tags.get(
                        "addr:street"
                    ),

                "numero":
                    tags.get(
                        "addr:housenumber"
                    ),

                "telefone":
                    (
                        tags.get("phone")
                        or tags.get(
                            "contact:phone"
                        )
                    ),

                "site":
                    (
                        tags.get("website")
                        or tags.get(
                            "contact:website"
                        )
                    ),

                "osm_tipo":
                    elemento.get(
                        "type"
                    ),

                "osm_id":
                    elemento.get(
                        "id"
                    )
            })


        lugares.sort(
            key=lambda lugar:
                lugar[
                    "distancia_m"
                ]
        )


        return lugares[
            :limite
        ]