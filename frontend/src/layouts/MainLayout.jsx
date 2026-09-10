import { useCallback, useEffect, useState } from "react";
import { Outlet } from "react-router-dom";
import Sidebar from "../components/Sidebar";
import CommandCenter from "../components/CommandCenter";

function MainLayout() {
    const [conversaSelecionada, setConversaSelecionada] = useState(null);
    const [atualizarConversas, setAtualizarConversas] = useState(0);
    const [recolhida, setRecolhida] = useState(() => localStorage.getItem("ara.sidebar") === "collapsed");
    const [commandAberto, setCommandAberto] = useState(false);
    const [tema, setTemaState] = useState(() => localStorage.getItem("ara.theme") || "dark");

    function conversaCriada() {
        setAtualizarConversas((valor) => valor + 1);
    }

    const setTema = useCallback((novoTema) => {
        setTemaState(novoTema);
        localStorage.setItem("ara.theme", novoTema);
    }, []);

    useEffect(() => {
        document.documentElement.dataset.theme = tema;
    }, [tema]);

    useEffect(() => {
        localStorage.setItem("ara.sidebar", recolhida ? "collapsed" : "open");
    }, [recolhida]);

    useEffect(() => {
        function atalho(event) {
            if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "k") {
                event.preventDefault();
                setCommandAberto((aberto) => !aberto);
            }
        }
        window.addEventListener("keydown", atalho);
        return () => window.removeEventListener("keydown", atalho);
    }, []);

    return (
        <div className="app ara-app">
            <Sidebar
                conversaSelecionada={conversaSelecionada}
                setConversaSelecionada={setConversaSelecionada}
                atualizarConversas={atualizarConversas}
                conversaCriada={conversaCriada}
                recolhida={recolhida}
                setRecolhida={setRecolhida}
                onOpenCommand={() => setCommandAberto(true)}
            />

            <div className="ara-workspace">
                <Outlet context={{
                    conversaSelecionada,
                    setConversaSelecionada,
                    conversaCriada,
                    tema,
                    setTema,
                    openCommand: () => setCommandAberto(true)
                }} />
            </div>

            <CommandCenter aberto={commandAberto} onClose={() => setCommandAberto(false)} />
        </div>
    );
}

export default MainLayout;
