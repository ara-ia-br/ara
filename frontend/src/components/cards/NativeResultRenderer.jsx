import WeatherCard from "./WeatherCard";
import RouteMapCard from "./RouteMapCard";
import NearbyCard from "./NearbyCard";


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


        case "rota":
            return (
                <RouteMapCard
                    dados={visualizacao}
                />
            );


        case "lugares_proximos":
            return (
                <NearbyCard
                    dados={visualizacao}
                />
            );


        default:
            return null;
    }
}


export default NativeResultRenderer;