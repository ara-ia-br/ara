import { useCallback, useEffect, useState } from "react";
import { Outlet } from "react-router-dom";
import Sidebar from "../components/Sidebar";
import CommandCenter from "../components/CommandCenter";

function MainLayout() {
    const [conversaSelecionada, setConversaSelecionada] = useState(null);
    const [atualizarConversas, setAtualizarConversas] = useState(0);
    const [recolhida, setRecolhida] = useState(() => localStorage.getItem("ara.sidebar") === "collapsed");
    const [commandAberto, setCommandAberto] = useState(false);
    const [tema, setTemaState] = useState("dark");
    const [cor, setCorState] = useState(() => localStorage.getItem("ara.accent") || "mint");
    const [logoChat, setLogoChatState] = useState(() => localStorage.getItem("ara.chatLogo") || "1");

    function conversaCriada() {
        setAtualizarConversas((valor) => valor + 1);
    }

    const setTema = useCallback((novoTema) => {
        setTemaState(novoTema);
        localStorage.setItem("ara.theme", novoTema);
    }, []);

    useEffect(() => {
        document.documentElement.dataset.theme = "dark";
        document.documentElement.dataset.accent = cor;
        document.documentElement.dataset.chatLogo = logoChat;
        localStorage.setItem("ara.accent", cor);
        localStorage.setItem("ara.chatLogo", logoChat);
    }, [cor, logoChat]);

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
                    cor,
                    setCor: setCorState,
                    logoChat,
                    setLogoChat: setLogoChatState,
                    openCommand: () => setCommandAberto(true)
                }} />
            </div>

            <CommandCenter aberto={commandAberto} onClose={() => setCommandAberto(false)} />
        </div>
    );
}

export default MainLayout;
