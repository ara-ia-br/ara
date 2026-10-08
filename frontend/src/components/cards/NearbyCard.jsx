import {
    useEffect,
    useRef
} from "react";

import {
    LngLatBounds,
    Map,
    Marker,
    NavigationControl,
    Popup,
    setWorkerUrl
} from "maplibre-gl";

import workerUrl from "maplibre-gl/dist/maplibre-gl-worker.mjs?worker&url";

import "maplibre-gl/dist/maplibre-gl.css";
import "./NearbyCard.css";


setWorkerUrl(workerUrl);


function NearbyCard({
    dados
}) {

    const mapaRef = useRef(null);
    const instanciaMapaRef = useRef(null);


    const origem = (
        dados?.origem
        || {}
    );

    const lugares = (
        Array.isArray(dados?.lugares)
            ? dados.lugares
            : []
    );


    const coordenadaValida = (
        latitude,
        longitude
    ) => {

        const lat = Number(latitude);
        const lon = Number(longitude);

        return (
            Number.isFinite(lat)
            && Number.isFinite(lon)
        );
    };


    const criarPopup = lugar => {

        const container = document.createElement("div");
        container.className = "nearby-popup";


        const titulo = document.createElement("strong");

        titulo.textContent = (
            lugar.nome
            || "Local"
        );

        container.appendChild(titulo);


        if (lugar.categoria) {

            const categoria = document.createElement("span");

            categoria.textContent = lugar.categoria;

            container.appendChild(categoria);
        }


        if (lugar.distancia_m != null) {

            const distancia = document.createElement("span");

            const valor = Number(
                lugar.distancia_m
            );

            if (Number.isFinite(valor)) {

                distancia.textContent = (
                    valor >= 1000
                        ? `${(valor / 1000)
                            .toFixed(1)
                            .replace(".", ",")} km`
                        : `${Math.round(valor)} m`
                );

                container.appendChild(distancia);
            }
        }


        const partesEndereco = [
            lugar.endereco,
            lugar.numero
        ].filter(Boolean);


        if (partesEndereco.length > 0) {

            const endereco = document.createElement("span");

            endereco.textContent = (
                partesEndereco.join(", ")
            );

            container.appendChild(endereco);
        }


        return container;
    };


    useEffect(() => {

        if (!mapaRef.current) {
            return;
        }


        const lugaresValidos = lugares.filter(
            lugar => coordenadaValida(
                lugar.latitude,
                lugar.longitude
            )
        );


        const origemValida = coordenadaValida(
            origem.latitude,
            origem.longitude
        );


        if (
            !origemValida
            && lugaresValidos.length === 0
        ) {
            return;
        }


        const centro = origemValida
            ? [
                Number(origem.longitude),
                Number(origem.latitude)
            ]
            : [
                Number(lugaresValidos[0].longitude),
                Number(lugaresValidos[0].latitude)
            ];


        const mapa = new Map({

            container:
                mapaRef.current,

            style:
                "https://tiles.openfreemap.org/styles/liberty",

            center:
                centro,

            zoom:
                14,

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

                const bounds = new LngLatBounds();


                // =========================================
                // POSIÇÃO DO USUÁRIO
                // =========================================

                if (origemValida) {

                    const coordenadasOrigem = [
                        Number(origem.longitude),
                        Number(origem.latitude)
                    ];


                    new Marker({
                        color: "#2563eb"
                    })
                        .setLngLat(
                            coordenadasOrigem
                        )
                        .setPopup(
                            new Popup({
                                offset: 20
                            })
                                .setText(
                                    "Sua localização"
                                )
                        )
                        .addTo(mapa);


                    bounds.extend(
                        coordenadasOrigem
                    );
                }


                // =========================================
                // LUGARES
                // =========================================

                lugaresValidos.forEach(
                    lugar => {

                        const coordenadasLugar = [
                            Number(lugar.longitude),
                            Number(lugar.latitude)
                        ];


                        const popup = new Popup({
                            offset: 20
                        })
                            .setDOMContent(
                                criarPopup(lugar)
                            );


                        new Marker({
                            color: "#dc2626"
                        })
                            .setLngLat(
                                coordenadasLugar
                            )
                            .setPopup(
                                popup
                            )
                            .addTo(
                                mapa
                            );


                        bounds.extend(
                            coordenadasLugar
                        );
                    }
                );


                // =========================================
                // ENQUADRAR RESULTADOS
                // =========================================

                if (!bounds.isEmpty()) {

                    mapa.fitBounds(
                        bounds,
                        {
                            padding: 55,
                            maxZoom: 15,
                            duration: 700
                        }
                    );
                }
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
        || lugares.length === 0
    ) {
        return null;
    }


    const formatarDistancia = distancia => {

        const valor = Number(distancia);

        if (!Number.isFinite(valor)) {
            return null;
        }


        if (valor >= 1000) {

            return (
                `${(valor / 1000)
                    .toFixed(1)
                    .replace(".", ",")} km`
            );
        }


        return `${Math.round(valor)} m`;
    };


    return (
        <div className="nearby-card">

            <div className="nearby-card-header">

                <div>

                    <div className="nearby-card-title">
                        Lugares próximos
                    </div>

                    {
                        dados.categoria
                        && (
                            <div className="nearby-card-category">
                                {dados.categoria}
                            </div>
                        )
                    }

                </div>


                <div className="nearby-card-count">

                    {lugares.length}

                    {
                        lugares.length === 1
                            ? " resultado"
                            : " resultados"
                    }

                </div>

            </div>


            <div
                ref={mapaRef}
                className="nearby-map"
            />


            <div className="nearby-list">

                {
                    lugares.map(
                        (
                            lugar,
                            index
                        ) => {

                            const distancia = (
                                formatarDistancia(
                                    lugar.distancia_m
                                )
                            );


                            const endereco = [
                                lugar.endereco,
                                lugar.numero
                            ]
                                .filter(Boolean)
                                .join(", ");


                            return (
                                <div
                                    key={
                                        lugar.osm_id
                                        || `${lugar.nome}-${index}`
                                    }
                                    className="nearby-item"
                                >

                                    <div className="nearby-item-number">
                                        {index + 1}
                                    </div>


                                    <div className="nearby-item-content">

                                        <strong>
                                            {
                                                lugar.nome
                                                || "Local"
                                            }
                                        </strong>


                                        {
                                            lugar.categoria
                                            && (
                                                <span>
                                                    {lugar.categoria}
                                                </span>
                                            )
                                        }


                                        {
                                            endereco
                                            && (
                                                <small>
                                                    {endereco}
                                                </small>
                                            )
                                        }

                                    </div>


                                    {
                                        distancia
                                        && (
                                            <div className="nearby-item-distance">
                                                {distancia}
                                            </div>
                                        )
                                    }

                                </div>
                            );
                        }
                    )
                }

            </div>


            <div className="nearby-card-footer">

                <span>
                    {
                        dados.raio_m
                            ? `Raio de busca: ${dados.raio_m} m`
                            : "Resultados próximos da sua localização"
                    }
                </span>

                <span>
                    OpenStreetMap
                </span>

            </div>

        </div>
    );
}


export default NearbyCard;