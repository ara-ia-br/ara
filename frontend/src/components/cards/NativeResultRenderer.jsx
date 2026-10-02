import WeatherCard from "./WeatherCard";


function NativeResultRenderer({
    visualizacao
}) {

    if (
        !visualizacao
        || typeof visualizacao !== "object"
    ) {
        return null;
    }

    switch (visualizacao.tipo) {

        case "clima":
            return (
                <WeatherCard
                    dados={visualizacao}
                />
            );

        default:
            return null;
    }
}


export default NativeResultRenderer;