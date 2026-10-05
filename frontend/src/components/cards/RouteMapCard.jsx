import {
    useEffect,
    useRef
} from "react";

import {
    Map,
    Marker,
    NavigationControl,
    setWorkerUrl
} from "maplibre-gl";

import workerUrl from "maplibre-gl/dist/maplibre-gl-worker.mjs?worker&url";

import "maplibre-gl/dist/maplibre-gl.css";
import "./RouteMapCard.css";


setWorkerUrl(workerUrl);


function RouteMapCard({
    dados
}) {

    const mapaRef = useRef(null);
    const instanciaMapaRef = useRef(null);


    const origem = (
        dados?.origem
        || {}
    );

    const destino = (
        dados?.destino
        || {}
    );

    const geometria = (
        dados?.geometria
        || null
    );

    const coordenadas = (
        geometria?.coordinates
        || []
    );


    useEffect(() => {

        if (!mapaRef.current) {
            return;
        }

        if (
            !Array.isArray(coordenadas)
            || coordenadas.length < 2
        ) {
            return;
        }


        const primeira = coordenadas[0];


        const mapa = new Map({

            container:
                mapaRef.current,

            style:
                "https://tiles.openfreemap.org/styles/liberty",

            center:
                primeira,

            zoom:
                12,

            attributionControl:
                true
        });


        instanciaMapaRef.current = mapa;


        mapa.addControl(
            new NavigationControl({
                showCompass: true,
                showZoom: true
            }),
            "top-right"
        );


        mapa.on(
            "load",
            () => {

                // =========================================
                // ROTA
                // =========================================

                mapa.addSource(
                    "ara-route",
                    {
                        type: "geojson",

                        data: {
                            type:
                                "Feature",

                            properties:
                                {},

                            geometry:
                                geometria
                        }
                    }
                );


                mapa.addLayer({
                    id:
                        "ara-route-line",

                    type:
                        "line",

                    source:
                        "ara-route",

                    layout: {
                        "line-cap":
                            "round",

                        "line-join":
                            "round"
                    },

                    paint: {
                        "line-color":
                            "#2563eb",

                        "line-width":
                            6,

                        "line-opacity":
                            0.9
                    }
                });


                // =========================================
                // ORIGEM
                // =========================================

                if (
                    origem.longitude != null
                    && origem.latitude != null
                ) {

                    new Marker({
                        color: "#16a34a"
                    })
                        .setLngLat([
                            origem.longitude,
                            origem.latitude
                        ])
                        .addTo(mapa);
                }


                // =========================================
                // DESTINO
                // =========================================

                if (
                    destino.longitude != null
                    && destino.latitude != null
                ) {

                    new Marker({
                        color: "#dc2626"
                    })
                        .setLngLat([
                            destino.longitude,
                            destino.latitude
                        ])
                        .addTo(mapa);
                }


                // =========================================
                // ENQUADRAR ROTA
                // =========================================

                const longitudes = (
                    coordenadas.map(
                        ponto => ponto[0]
                    )
                );

                const latitudes = (
                    coordenadas.map(
                        ponto => ponto[1]
                    )
                );


                const minLon = Math.min(
                    ...longitudes
                );

                const maxLon = Math.max(
                    ...longitudes
                );

                const minLat = Math.min(
                    ...latitudes
                );

                const maxLat = Math.max(
                    ...latitudes
                );


                mapa.fitBounds(
                    [
                        [
                            minLon,
                            minLat
                        ],
                        [
                            maxLon,
                            maxLat
                        ]
                    ],
                    {
                        padding: 45,
                        duration: 700
                    }
                );
            }
        );


        return () => {

            instanciaMapaRef.current = null;

            mapa.remove();
        };

    }, [
        dados
    ]);


    if (
        !dados
        || !geometria
        || coordenadas.length < 2
    ) {
        return null;
    }


    const distancia = (
        Number(
            dados.distancia_km
        )
    );

    const duracao = (
        Number(
            dados.duracao_min
        )
    );


    const distanciaFormatada = (
        Number.isFinite(distancia)
            ? distancia
                .toFixed(1)
                .replace(".", ",")
            : null
    );


    const origemNome = (
        origem.nome
        || origem.consulta
        || "Origem"
    );

    const destinoNome = (
        destino.nome
        || destino.consulta
        || "Destino"
    );


    return (
        <div className="route-card">

            <div className="route-card-header">

                <div className="route-card-title">
                    Rota
                </div>

                <div className="route-card-summary">

                    {
                        distanciaFormatada
                        && (
                            <span>
                                {distanciaFormatada} km
                            </span>
                        )
                    }

                    {
                        Number.isFinite(duracao)
                        && (
                            <span>
                                ≈ {Math.round(duracao)} min
                            </span>
                        )
                    }

                </div>

            </div>


            <div className="route-card-locations">

                <div className="route-location">

                    <span
                        className={
                            "route-location-dot "
                            + "route-location-origin"
                        }
                    />

                    <div>
                        <small>
                            Origem
                        </small>

                        <strong>
                            {origemNome}
                        </strong>
                    </div>

                </div>


                <div className="route-location">

                    <span
                        className={
                            "route-location-dot "
                            + "route-location-destination"
                        }
                    />

                    <div>
                        <small>
                            Destino
                        </small>

                        <strong>
                            {destinoNome}
                        </strong>
                    </div>

                </div>

            </div>


            <div
                ref={mapaRef}
                className="route-map"
            />


            <div className="route-card-footer">

                <span>
                    Tempo estimado sem considerar trânsito.
                </span>

                <span>
                    OSRM · OpenStreetMap
                </span>

            </div>

        </div>
    );
}


export default RouteMapCard;