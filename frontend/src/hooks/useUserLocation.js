import {
    useCallback,
    useEffect,
    useRef,
    useState
} from "react";


function useUserLocation() {

    const watchIdRef = useRef(null);

    const ultimaLocalizacaoBoaRef =
        useRef(null);


    const [
        location,
        setLocation
    ] = useState(null);


    const [
        error,
        setError
    ] = useState(null);


    const [
        tracking,
        setTracking
    ] = useState(false);


    // =========================================================
    // NORMALIZAR POSIÇÃO
    // =========================================================

    const criarLocalizacao = useCallback(
        (position) => {

            return {
                latitude:
                    position.coords.latitude,

                longitude:
                    position.coords.longitude,

                accuracy:
                    position.coords.accuracy,

                timestamp:
                    position.timestamp
            };
        },
        []
    );


    // =========================================================
    // VALIDAR COORDENADAS
    // =========================================================

    const coordenadasValidas = useCallback(
        (dados) => {

            const latitude = Number(
                dados?.latitude
            );

            const longitude = Number(
                dados?.longitude
            );


            return (
                Number.isFinite(latitude)
                && Number.isFinite(longitude)
                && latitude >= -90
                && latitude <= 90
                && longitude >= -180
                && longitude <= 180
            );
        },
        []
    );


    // =========================================================
    // ATUALIZAR LOCALIZAÇÃO
    // =========================================================

    const atualizarLocalizacao = useCallback(
        (dados) => {

            if (
                !coordenadasValidas(
                    dados
                )
            ) {

                return false;
            }


            const accuracy = Number(
                dados.accuracy
            );


            const atual =
                ultimaLocalizacaoBoaRef.current;


            /*
             * Se já existe uma localização boa
             * e chega uma leitura drasticamente
             * pior, preserva a melhor posição.
             */
            if (
                atual
                && Number.isFinite(
                    atual.accuracy
                )
                && atual.accuracy <= 1000
                && Number.isFinite(
                    accuracy
                )
                && accuracy >= 5000
            ) {

                console.warn(
                    "[LOCALIZAÇÃO] "
                    + "Leitura muito imprecisa ignorada:",
                    Math.round(
                        accuracy
                    ),
                    "m"
                );

                return false;
            }


            /*
             * Coordenadas válidas são aceitas.
             *
             * Uma accuracy alta significa apenas
             * que a posição é aproximada.
             */
            setLocation(
                dados
            );


            /*
             * Guarda separadamente a última
             * localização considerada boa.
             */
            if (
                Number.isFinite(
                    accuracy
                )
                && accuracy <= 1000
            ) {

                ultimaLocalizacaoBoaRef.current =
                    dados;
            }


            setError(
                null
            );


            return true;
        },
        [
            coordenadasValidas
        ]
    );


    // =========================================================
    // TRATAR ERRO
    // =========================================================

    const mensagemErroGeolocalizacao =
        useCallback(
            (geolocationError) => {

                if (
                    geolocationError.code
                    === geolocationError.PERMISSION_DENIED
                ) {

                    return (
                        "A permissão de localização "
                        + "foi negada."
                    );
                }


                if (
                    geolocationError.code
                    === geolocationError.POSITION_UNAVAILABLE
                ) {

                    return (
                        "Sua localização não está "
                        + "disponível."
                    );
                }


                if (
                    geolocationError.code
                    === geolocationError.TIMEOUT
                ) {

                    return (
                        "A localização demorou demais "
                        + "para responder."
                    );
                }


                return (
                    "Não foi possível obter "
                    + "sua localização."
                );
            },
            []
        );


    // =========================================================
    // PARAR RASTREAMENTO
    // =========================================================

    const stopTracking = useCallback(
        () => {

            if (
                watchIdRef.current !== null
                && navigator.geolocation
            ) {

                navigator.geolocation.clearWatch(
                    watchIdRef.current
                );

                watchIdRef.current = null;
            }


            setTracking(
                false
            );
        },
        []
    );


    // =========================================================
    // LOCALIZAÇÃO ÚNICA
    // =========================================================

    const getCurrentLocation = useCallback(
        () => {

            return new Promise(
                (
                    resolve,
                    reject
                ) => {

                    if (!navigator.geolocation) {

                        reject(
                            new Error(
                                "Seu navegador não oferece "
                                + "suporte à localização."
                            )
                        );

                        return;
                    }


                    navigator.geolocation
                        .getCurrentPosition(

                            (position) => {

                                const dados =
                                    criarLocalizacao(
                                        position
                                    );


                                if (
                                    !coordenadasValidas(
                                        dados
                                    )
                                ) {

                                    const mensagem = (
                                        "O navegador retornou "
                                        + "coordenadas inválidas."
                                    );


                                    setError(
                                        mensagem
                                    );


                                    reject(
                                        new Error(
                                            mensagem
                                        )
                                    );

                                    return;
                                }


                                atualizarLocalizacao(
                                    dados
                                );


                                resolve(
                                    dados
                                );
                            },

                            (geolocationError) => {

                                const mensagem =
                                    mensagemErroGeolocalizacao(
                                        geolocationError
                                    );


                                setError(
                                    mensagem
                                );


                                reject(
                                    new Error(
                                        mensagem
                                    )
                                );
                            },

                            {
                                enableHighAccuracy:
                                    true,

                                timeout:
                                    15000,

                                maximumAge:
                                    5000
                            }
                        );
                }
            );
        },
        [
            criarLocalizacao,
            coordenadasValidas,
            atualizarLocalizacao,
            mensagemErroGeolocalizacao
        ]
    );


    // =========================================================
    // INICIAR RASTREAMENTO
    // =========================================================

    const startTracking = useCallback(
        () => {

            if (!navigator.geolocation) {

                setError(
                    "Seu navegador não oferece "
                    + "suporte à localização."
                );

                return;
            }


            if (
                watchIdRef.current !== null
            ) {

                return;
            }


            setError(
                null
            );


            watchIdRef.current =
                navigator.geolocation.watchPosition(

                    (position) => {

                        const novaLocalizacao =
                            criarLocalizacao(
                                position
                            );


                        setTracking(
                            true
                        );


                        atualizarLocalizacao(
                            novaLocalizacao
                        );
                    },

                    (geolocationError) => {

                        const mensagem =
                            mensagemErroGeolocalizacao(
                                geolocationError
                            );


                        setError(
                            mensagem
                        );


                        /*
                         * Se a permissão foi negada,
                         * o rastreamento efetivamente
                         * não pode continuar.
                         */
                        if (
                            geolocationError.code
                            === geolocationError.PERMISSION_DENIED
                        ) {

                            setTracking(
                                false
                            );

                            watchIdRef.current =
                                null;
                        }
                    },

                    {
                        enableHighAccuracy:
                            true,

                        timeout:
                            15000,

                        maximumAge:
                            5000
                    }
                );
        },
        [
            criarLocalizacao,
            atualizarLocalizacao,
            mensagemErroGeolocalizacao
        ]
    );


    // =========================================================
    // CLEANUP
    // =========================================================

    useEffect(
        () => {

            return () => {

                stopTracking();
            };
        },
        [
            stopTracking
        ]
    );


    // =========================================================
    // RETORNO
    // =========================================================

    return {
        location,
        error,
        tracking,
        startTracking,
        stopTracking,
        getCurrentLocation
    };
}


export default useUserLocation;