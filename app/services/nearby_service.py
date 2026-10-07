from __future__ import annotations

from math import atan2, cos, radians, sin, sqrt
from typing import Any

import httpx

import asyncio


class NearbyService:
    _URLS = [
        "https://overpass.private.coffee/api/interpreter",
        "https://maps.mail.ru/osm/tools/overpass/api/interpreter",
        "https://overpass-api.de/api/interpreter",
    ]

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


    _NOMINATIM_CATEGORIAS = {
        "restaurante": "restaurant",
        "lanchonete": "fast_food",
        "cafe": "cafe",
        "bar": "bar",
        "farmacia": "pharmacy",
        "hospital": "hospital",
        "supermercado": "supermarket",
        "mercado": "supermarket",
        "posto": "fuel",
        "banco": "bank",
        "atm": "atm",
        "academia": "fitness_centre",
        "parque": "park",
        "hotel": "hotel",
        "estacionamento": "parking",
    }

    _NOMINATIM_URL = (
        "https://nominatim.openstreetmap.org/search"
    )


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

    async def _buscar_nominatim_generico(
        self,
        latitude: float,
        longitude: float,
        raio_m: int,
        limite: int
    ) -> list[dict[str, Any]]:

        categorias = [
            "restaurante",
            "farmacia",
            "supermercado",
            "cafe"
        ]

        encontrados = []

        for indice, categoria in enumerate(
            categorias
        ):

            if indice > 0:
                await asyncio.sleep(1.1)

            try:

                resultado = (
                    await self._buscar_nominatim(
                        latitude=latitude,
                        longitude=longitude,
                        categoria=categoria,
                        raio_m=raio_m,
                        limite=4
                    )
                )

                encontrados.extend(
                    resultado
                )

            except (
                httpx.HTTPError,
                TimeoutError
            ) as erro:

                print(
                    "[NEARBY] Nominatim "
                    f"falhou em {categoria}: "
                    f"{erro!r}"
                )

                continue

        # ==============================================
        # REMOVE DUPLICADOS
        # ==============================================

        unicos = {}

        for lugar in encontrados:

            osm_tipo = lugar.get(
                "osm_tipo"
            )

            osm_id = lugar.get(
                "osm_id"
            )

            if (
                osm_tipo
                and osm_id
            ):
                chave = (
                    osm_tipo,
                    osm_id
                )

            else:
                chave = (
                    lugar.get("nome"),
                    lugar.get("latitude"),
                    lugar.get("longitude")
                )

            unicos[chave] = lugar

        lugares = list(
            unicos.values()
        )

        # ==============================================
        # ORDENA POR DISTÂNCIA
        # ==============================================

        lugares.sort(
            key=lambda lugar:
                lugar.get(
                    "distancia_m",
                    float("inf")
                )
        )

        return lugares[:limite]


    async def _executar_query(
        self,
        query: str
    ) -> dict[str, Any]:

        ultimo_erro = None

        timeout = httpx.Timeout(
            20.0,
            connect=8.0
        )

        async with httpx.AsyncClient(
            timeout=timeout,
            headers=self._HEADERS
        ) as client:

            for url in self._URLS:

                for tentativa in range(2):

                    try:

                        resposta = await client.post(
                            url,
                            data={
                                "data":
                                    query
                            }
                        )

                        resposta.raise_for_status()

                        dados = resposta.json()

                        if not isinstance(
                            dados,
                            dict
                        ):
                            raise ValueError(
                                "Resposta inválida "
                                "do serviço de mapas."
                            )

                        return dados


                    except (
                        httpx.ConnectTimeout,
                        httpx.ReadTimeout,
                        httpx.ConnectError
                    ) as erro:

                        ultimo_erro = erro


                    except (
                        httpx.HTTPStatusError
                    ) as erro:

                        ultimo_erro = erro

                        status = (
                            erro.response.status_code
                        )

                        if status not in {
                            429,
                            500,
                            502,
                            503,
                            504
                        }:

                            raise


                    if tentativa == 0:

                        await asyncio.sleep(
                            1.0
                        )


        print(
            "[NEARBY] Todos os servidores "
            "Overpass falharam:",
            repr(ultimo_erro)
        )

        raise RuntimeError(
            "O serviço de lugares próximos "
            "está temporariamente indisponível."
        )

    async def _buscar_nominatim(
        self,
        latitude: float,
        longitude: float,
        categoria: str,
        raio_m: int,
        limite: int
    ) -> list[dict[str, Any]]:

        termo = self._NOMINATIM_CATEGORIAS.get(
            categoria
        )

        if not termo:
            return []

        # Aproximação suficiente para uma viewbox local.
        delta_lat = raio_m / 111_320

        cos_lat = max(
            cos(radians(latitude)),
            0.1
        )

        delta_lon = (
            raio_m
            / (
                111_320
                * cos_lat
            )
        )

        oeste = longitude - delta_lon
        leste = longitude + delta_lon

        norte = latitude + delta_lat
        sul = latitude - delta_lat

        parametros = {
            "format": "jsonv2",

            "q":
                f"[{termo}]",

            "viewbox":
                (
                    f"{oeste},"
                    f"{norte},"
                    f"{leste},"
                    f"{sul}"
                ),

            "bounded":
                1,

            "limit":
                min(
                    max(limite * 2, 10),
                    20
                ),

            "addressdetails":
                1,

            "extratags":
                1,

            "accept-language":
                "pt-BR"
        }

        async with httpx.AsyncClient(
            timeout=15.0,
            headers=self._HEADERS
        ) as client:

            resposta = await client.get(
                self._NOMINATIM_URL,
                params=parametros
            )

        resposta.raise_for_status()

        dados = resposta.json()

        lugares = []

        chaves = set()

        for item in dados:

            lat = item.get("lat")
            lon = item.get("lon")

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

            # A viewbox é retangular.
            # Garantimos aqui o raio circular real.
            if distancia > raio_m:
                continue

            nome = (
                item.get("name")
                or (
                    item.get("display_name", "")
                    .split(",")[0]
                    .strip()
                )
            )

            if not nome:
                continue

            chave = (
                nome.lower(),
                round(lat, 5),
                round(lon, 5)
            )

            if chave in chaves:
                continue

            chaves.add(chave)

            endereco = (
                item.get("address")
                or {}
            )

            extratags = (
                item.get("extratags")
                or {}
            )

            lugares.append({
                "nome":
                    nome,

                "categoria":
                    self._categoria_elemento(
                        {
                            "amenity":
                                termo,

                            "shop":
                                termo,

                            "leisure":
                                termo,

                            "tourism":
                                termo
                        }
                    ),

                "latitude":
                    lat,

                "longitude":
                    lon,

                "distancia_m":
                    round(distancia),

                "endereco":
                    (
                        endereco.get("road")
                        or endereco.get(
                            "pedestrian"
                        )
                    ),

                "numero":
                    endereco.get(
                        "house_number"
                    ),

                "telefone":
                    (
                        extratags.get("phone")
                        or extratags.get(
                            "contact:phone"
                        )
                    ),

                "site":
                    (
                        extratags.get("website")
                        or extratags.get(
                            "contact:website"
                        )
                    ),

                "osm_tipo":
                    item.get(
                        "osm_type"
                    ),

                "osm_id":
                    item.get(
                        "osm_id"
                    )
            })

        lugares.sort(
            key=lambda lugar:
                lugar["distancia_m"]
        )

        return lugares[:limite]

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

        if categoria is None:
            raio_m = min(
                raio_m,
                1000
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
                "way"
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
            "[timeout:15];"
            "("
            + "".join(
                consultas
            )
            + ");"
            "out center tags;"
        )


        try:

            dados = await self._executar_query(
                query
            )

        except RuntimeError:

            if categoria:
                print(
                    "[NEARBY] Overpass indisponível. "
                    "Usando fallback Nominatim."
                )

                return await self._buscar_nominatim(
                    latitude=latitude,
                    longitude=longitude,
                    categoria=categoria,
                    raio_m=raio_m,
                    limite=limite
                )

            print(
                "[NEARBY] Overpass indisponível. "
                "Usando fallback Nominatim genérico."
            )

            return await self._buscar_nominatim_generico(
                latitude=latitude,
                longitude=longitude,
                raio_m=raio_m,
                limite=limite
            )





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