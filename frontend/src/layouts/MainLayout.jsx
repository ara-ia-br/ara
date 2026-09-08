import { useState } from "react";
import { Outlet } from "react-router-dom";

import Sidebar from "../components/Sidebar";


function MainLayout() {

    const [
        conversaSelecionada,
        setConversaSelecionada
    ] = useState(null);

    const [
        atualizarConversas,
        setAtualizarConversas
    ] = useState(0);


    function conversaCriada() {

        setAtualizarConversas(
            (valor) => valor + 1
        );
    }


    return (
        <div className="app">

            <Sidebar
                conversaSelecionada={
                    conversaSelecionada
                }
                setConversaSelecionada={
                    setConversaSelecionada
                }
                atualizarConversas={
                    atualizarConversas
                }
                conversaCriada={
                    conversaCriada
                }
            />

            <Outlet
                context={{
                    conversaSelecionada,
                    setConversaSelecionada,
                    conversaCriada
                }}
            />

        </div>
    );
}


export default MainLayout;