import {
    CloudRain,
    Droplets,
    Wind
} from "lucide-react";


function formatarNumero(
    valor,
    casas = 0
) {

    const numero = Number(valor);

    if (!Number.isFinite(numero)) {
        return "—";
    }

    return numero.toLocaleString(
        "pt-BR",
        {
            minimumFractionDigits: casas,
            maximumFractionDigits: casas
        }
    );
}


function formatarHorario(
    valor
) {

    if (!valor) {
        return "";
    }

    const data = new Date(valor);

    if (
        Number.isNaN(
            data.getTime()
        )
    ) {
        return "";
    }

    return data.toLocaleTimeString(
        "pt-BR",
        {
            hour: "2-digit",
            minute: "2-digit"
        }
    );
}


function WeatherChart({
    horas = []
}) {

    const pontos = horas.filter(
        item =>
            Number.isFinite(
                Number(
                    item?.temperatura_c
                )
            )
    );

    if (pontos.length < 2) {
        return null;
    }


    const largura = 720;
    const altura = 180;

    const esquerda = 30;
    const direita = 30;
    const topo = 28;
    const baixo = 38;


    const temperaturas = pontos.map(
        item =>
            Number(
                item.temperatura_c
            )
    );


    let minima = Math.min(
        ...temperaturas
    );

    let maxima = Math.max(
        ...temperaturas
    );


    if (minima === maxima) {
        minima -= 1;
        maxima += 1;
    }


    const larguraUtil = (
        largura
        - esquerda
        - direita
    );

    const alturaUtil = (
        altura
        - topo
        - baixo
    );


    const coordenadas = pontos.map(
        (
            item,
            indice
        ) => {

            const x = (
                esquerda
                + (
                    indice
                    / (
                        pontos.length
                        - 1
                    )
                )
                * larguraUtil
            );

            const proporcao = (
                (
                    Number(
                        item.temperatura_c
                    )
                    - minima
                )
                /
                (
                    maxima
                    - minima
                )
            );

            const y = (
                topo
                + alturaUtil
                - (
                    proporcao
                    * alturaUtil
                )
            );

            return {
                x,
                y,
                item
            };
        }
    );


    const path = coordenadas
        .map(
            (
                ponto,
                indice
            ) =>
                `${indice === 0 ? "M" : "L"} ${ponto.x} ${ponto.y}`
        )
        .join(" ");


    return (
        <div className="weather-chart-wrapper">

            <svg
                viewBox={`0 0 ${largura} ${altura}`}
                className="weather-chart"
            >

                <line
                    x1={esquerda}
                    y1={topo + alturaUtil}
                    x2={largura - direita}
                    y2={topo + alturaUtil}
                    className="weather-chart-grid"
                />

                <path
                    d={path}
                    className="weather-chart-line"
                />

                {
                    coordenadas.map(
                        (
                            ponto,
                            indice
                        ) => (
                            <g
                                key={
                                    `${ponto.item.horario}-${indice}`
                                }
                            >

                                <circle
                                    cx={ponto.x}
                                    cy={ponto.y}
                                    r="4"
                                    className="weather-chart-dot"
                                />

                                <text
                                    x={ponto.x}
                                    y={ponto.y - 12}
                                    textAnchor="middle"
                                    className="weather-chart-temperature"
                                >
                                    {
                                        formatarNumero(
                                            ponto.item.temperatura_c,
                                            0
                                        )
                                    }°
                                </text>

                                {
                                    (
                                        indice % 2 === 0
                                        || indice
                                        === coordenadas.length - 1
                                    )
                                    && (
                                        <text
                                            x={ponto.x}
                                            y={altura - 8}
                                            textAnchor="middle"
                                            className="weather-chart-hour"
                                        >
                                            {
                                                formatarHorario(
                                                    ponto.item.horario
                                                )
                                            }
                                        </text>
                                    )
                                }

                            </g>
                        )
                    )
                }

            </svg>

        </div>
    );
}


function WeatherCard({
    dados
}) {

    const local =
        dados?.local || {};

    const atual =
        dados?.atual || {};

    const horas =
        dados?.horas || [];


    const nomeLocal = (
        local.cidade
        || local.nome
        || "Local"
    );


    return (
        <section className="native-card weather-card">

            <header className="weather-card-header">

                <div>

                    <span className="native-card-kicker">
                        CLIMA
                    </span>

                    <h3>
                        {nomeLocal}
                    </h3>

                    <p>
                        {
                            atual.condicao
                            || "Condição atual"
                        }
                    </p>

                </div>

                <strong className="weather-current-temperature">

                    {
                        formatarNumero(
                            atual.temperatura_c,
                            1
                        )
                    }

                    <small>
                        °C
                    </small>

                </strong>

            </header>


            <WeatherChart
                horas={horas}
            />


            <div className="weather-card-metrics">

                <div>
                    <Droplets size={16} />

                    <span>
                        Umidade
                    </span>

                    <strong>
                        {
                            formatarNumero(
                                atual.umidade_percentual
                            )
                        }%
                    </strong>
                </div>


                <div>
                    <Wind size={16} />

                    <span>
                        Vento
                    </span>

                    <strong>
                        {
                            formatarNumero(
                                atual.vento_m_s,
                                1
                            )
                        } m/s
                    </strong>
                </div>


                <div>
                    <CloudRain size={16} />

                    <span>
                        Próx. hora
                    </span>

                    <strong>
                        {
                            formatarNumero(
                                atual.precipitacao_mm,
                                1
                            )
                        } mm
                    </strong>
                </div>

            </div>


            <small className="native-card-source">
                {
                    dados?.atribuicao
                    || "MET Norway"
                }
            </small>

        </section>
    );
}


export default WeatherCard;