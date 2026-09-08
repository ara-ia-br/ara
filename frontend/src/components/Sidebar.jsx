import { useEffect, useRef, useState } from "react";
import {useLocation, useNavigate} from "react-router-dom";

import {
    Archive,
    ListTodo,
    MessageSquare,
    MessageSquarePlus,
    MoreHorizontal,
    Pencil,
    RotateCcw,
    Settings,
    Trash2,
    User,
    X
} from "lucide-react";

import api from "../services/api";
import { useAuth } from "../context/AuthContext";


function Sidebar({
    conversaSelecionada,
    setConversaSelecionada,
    atualizarConversas,
    conversaCriada
}) {

    const { usuario, logout } = useAuth();

    const navigate = useNavigate();

    const location = useLocation();

    const [conversas, setConversas] = useState([]);
    const [conversasArquivadas, setConversasArquivadas] = useState([]);

    const [criando, setCriando] = useState(false);

    const [menuAberto, setMenuAberto] = useState(null);

    const [renomeando, setRenomeando] = useState(null);
    const [novoTitulo, setNovoTitulo] = useState("");

    const [mostrarArquivadas, setMostrarArquivadas] = useState(false);

    const menuRef = useRef(null);


    <div className="sidebar-navigation">

    <button
        className={
            location.pathname === "/chat"
                ? "sidebar-nav-item active"
                : "sidebar-nav-item"
        }
        onClick={() => navigate("/chat")}
    >
        <MessageSquare size={18} />

        <span>
            Chat
        </span>
    </button>

    <button
        className={
            location.pathname === "/tarefas"
                ? "sidebar-nav-item active"
                : "sidebar-nav-item"
        }
        onClick={() => navigate("/tarefas")}
    >
        <ListTodo size={18} />

        <span>
            Tarefas
        </span>
    </button>

</div>


    // =========================================================
    // CARREGAR CONVERSAS ATIVAS
    // =========================================================

    async function carregarConversas() {

        if (!usuario?.id_usuario) {
            return;
        }

        try {

            const resposta = await api.get(
                `/conversas/usuario/${usuario.id_usuario}`
            );

            setConversas(
                resposta.data
            );


            // Se não existe conversa selecionada,
            // seleciona automaticamente a primeira.
            if (
                !conversaSelecionada
                && resposta.data.length > 0
            ) {

                setConversaSelecionada(
                    resposta.data[0]
                );
            }


            // Atualiza os dados da conversa selecionada
            // caso título/data/status tenham mudado.
            if (conversaSelecionada) {

                const atualizada = resposta.data.find(
                    (conversa) =>
                        conversa.id_conversa
                        === conversaSelecionada.id_conversa
                );

                if (atualizada) {

                    setConversaSelecionada(
                        atualizada
                    );

                } else {

                    setConversaSelecionada(null);
                }
            }

        } catch (erro) {

            console.error(
                "Erro ao carregar conversas:",
                erro
            );
        }
    }


    // =========================================================
    // CARREGAR CONVERSAS ARQUIVADAS
    // =========================================================

    async function carregarArquivadas() {

        if (!usuario?.id_usuario) {
            return;
        }

        try {

            const resposta = await api.get(
                `/conversas/usuario/${usuario.id_usuario}/arquivadas`
            );

            setConversasArquivadas(
                resposta.data
            );

        } catch (erro) {

            console.error(
                "Erro ao carregar conversas arquivadas:",
                erro
            );
        }
    }


    // =========================================================
    // CRIAR NOVA CONVERSA
    // =========================================================

    async function criarNovaConversa() {

        if (
            criando
            || !usuario?.id_usuario
        ) {
            return;
        }

        setCriando(true);

        try {

            const resposta = await api.post(
                "/conversas",
                {
                    id_usuario: usuario.id_usuario,
                    titulo: "Nova conversa"
                }
            );

            setConversaSelecionada(
                resposta.data
            );

            conversaCriada();

        } catch (erro) {

            console.error(
                "Erro ao criar conversa:",
                erro
            );

        } finally {

            setCriando(false);
        }
    }


    // =========================================================
    // ABRIR / FECHAR MENU DE CONVERSA
    // =========================================================

    function alternarMenu(
        event,
        idConversa
    ) {

        event.stopPropagation();

        setMenuAberto(
            menuAberto === idConversa
                ? null
                : idConversa
        );
    }


    // =========================================================
    // RENOMEAR
    // =========================================================

    function iniciarRenomeacao(
        event,
        conversa
    ) {

        event.stopPropagation();

        setRenomeando(
            conversa.id_conversa
        );

        setNovoTitulo(
            conversa.titulo
        );

        setMenuAberto(null);
    }


    function cancelarRenomeacao() {

        setRenomeando(null);
        setNovoTitulo("");
    }


    async function salvarNovoTitulo(
        event,
        conversa
    ) {

        event.preventDefault();
        event.stopPropagation();

        const titulo = novoTitulo.trim();

        if (!titulo) {
            return;
        }

        try {

            const resposta = await api.patch(
                `/conversas/${conversa.id_conversa}/titulo`,
                {
                    titulo
                }
            );


            setConversas(
                (anteriores) =>
                    anteriores.map(
                        (item) =>
                            item.id_conversa
                            === conversa.id_conversa
                                ? resposta.data
                                : item
                    )
            );


            if (
                conversaSelecionada?.id_conversa
                === conversa.id_conversa
            ) {

                setConversaSelecionada(
                    resposta.data
                );
            }


            cancelarRenomeacao();

        } catch (erro) {

            console.error(
                "Erro ao renomear conversa:",
                erro
            );
        }
    }


    // =========================================================
    // ARQUIVAR
    // =========================================================

    async function arquivarConversa(
        event,
        conversa
    ) {

        event.stopPropagation();

        const confirmar = window.confirm(
            `Arquivar "${conversa.titulo}"?`
        );

        if (!confirmar) {
            return;
        }

        try {

            await api.patch(
                `/conversas/${conversa.id_conversa}/arquivar`
            );


            setConversas(
                (anteriores) =>
                    anteriores.filter(
                        (item) =>
                            item.id_conversa
                            !== conversa.id_conversa
                    )
            );


            if (
                conversaSelecionada?.id_conversa
                === conversa.id_conversa
            ) {

                setConversaSelecionada(null);
            }


            setMenuAberto(null);

            conversaCriada();

            if (mostrarArquivadas) {
                carregarArquivadas();
            }

        } catch (erro) {

            console.error(
                "Erro ao arquivar conversa:",
                erro
            );
        }
    }


    // =========================================================
    // RESTAURAR
    // =========================================================

    async function restaurarConversa(
        conversa
    ) {

        try {

            const resposta = await api.patch(
                `/conversas/${conversa.id_conversa}/restaurar`
            );


            setConversasArquivadas(
                (anteriores) =>
                    anteriores.filter(
                        (item) =>
                            item.id_conversa
                            !== conversa.id_conversa
                    )
            );


            await carregarConversas();

            setConversaSelecionada(
                resposta.data
            );

            conversaCriada();

        } catch (erro) {

            console.error(
                "Erro ao restaurar conversa:",
                erro
            );
        }
    }


    // =========================================================
    // EXCLUIR
    // =========================================================

    async function excluirConversa(
        event,
        conversa
    ) {

        event.stopPropagation();

        const confirmar = window.confirm(
            `Excluir definitivamente "${conversa.titulo}"?\n\n`
            + "Essa ação não poderá ser desfeita."
        );

        if (!confirmar) {
            return;
        }

        try {

            await api.delete(
                `/conversas/${conversa.id_conversa}`
            );


            setConversas(
                (anteriores) =>
                    anteriores.filter(
                        (item) =>
                            item.id_conversa
                            !== conversa.id_conversa
                    )
            );


            if (
                conversaSelecionada?.id_conversa
                === conversa.id_conversa
            ) {

                setConversaSelecionada(null);
            }


            setMenuAberto(null);

            conversaCriada();

        } catch (erro) {

            console.error(
                "Erro ao excluir conversa:",
                erro
            );

            alert(
                erro.response?.data?.detail
                || "Não foi possível excluir a conversa."
            );
        }
    }


    // =========================================================
    // MOSTRAR / ESCONDER ARQUIVADAS
    // =========================================================

    function alternarArquivadas() {

        const novoEstado = !mostrarArquivadas;

        setMostrarArquivadas(
            novoEstado
        );

        if (novoEstado) {
            carregarArquivadas();
        }
    }


    // =========================================================
    // CARREGAMENTO AUTOMÁTICO
    // =========================================================

    useEffect(
        () => {

            carregarConversas();

        },
        [
            atualizarConversas,
            usuario?.id_usuario
        ]
    );


    // =========================================================
    // FECHAR MENU AO CLICAR FORA
    // =========================================================

    useEffect(
        () => {

            function fecharMenu(event) {

                if (
                    menuRef.current
                    && !menuRef.current.contains(
                        event.target
                    )
                ) {

                    setMenuAberto(null);
                }
            }


            document.addEventListener(
                "mousedown",
                fecharMenu
            );


            return () => {

                document.removeEventListener(
                    "mousedown",
                    fecharMenu
                );
            };

        },
        []
    );


    return (
        <aside className="sidebar">

            {/* ==================================================
                CABEÇALHO
            ================================================== */}

            <div className="sidebar-header">

                <div className="logo">
                    J
                </div>

                <div>

                    <h1>
                        JARVIS
                    </h1>

                    <span>
                        Assistente pessoal
                    </span>

                </div>

            </div>


            {/* ==================================================
                NOVA CONVERSA
            ================================================== */}

            <button
                className="new-chat"
                onClick={criarNovaConversa}
                disabled={criando}
            >

                <MessageSquarePlus size={19} />

                {
                    criando
                        ? "Criando..."
                        : "Nova conversa"
                }

            </button>


            {/* ==================================================
                LISTA DE CONVERSAS
            ================================================== */}

            <div className="sidebar-section">

                <span className="section-title">
                    CONVERSAS
                </span>


                {
                    conversas.length === 0
                    && (
                        <div className="no-conversations">

                            Nenhuma conversa ainda.

                        </div>
                    )
                }


                {
                    conversas.map(
                        (conversa) => (

                            <div
                                key={conversa.id_conversa}
                                className="conversation-wrapper"
                            >

                                {
                                    renomeando
                                    === conversa.id_conversa
                                        ? (

                                            <form
                                                className="rename-conversation"
                                                onSubmit={
                                                    (event) =>
                                                        salvarNovoTitulo(
                                                            event,
                                                            conversa
                                                        )
                                                }
                                                onClick={
                                                    (event) =>
                                                        event.stopPropagation()
                                                }
                                            >

                                                <input
                                                    type="text"
                                                    value={novoTitulo}
                                                    onChange={
                                                        (event) =>
                                                            setNovoTitulo(
                                                                event.target.value
                                                            )
                                                    }
                                                    maxLength={200}
                                                    autoFocus
                                                />

                                                <button
                                                    type="button"
                                                    onClick={
                                                        cancelarRenomeacao
                                                    }
                                                    title="Cancelar"
                                                >
                                                    <X size={16} />
                                                </button>

                                            </form>

                                        )
                                        : (

                                            <button
                                                className={
                                                    conversaSelecionada
                                                        ?.id_conversa
                                                    === conversa.id_conversa

                                                        ? "conversation active"

                                                        : "conversation"
                                                }
                                                onClick={
                                                    () =>
                                                        setConversaSelecionada(
                                                            conversa
                                                        )
                                                }
                                            >

                                                <MessageSquare
                                                    size={17}
                                                />

                                                <span
                                                    className="conversation-title"
                                                >

                                                    {conversa.titulo}

                                                </span>


                                                <span
                                                    className="conversation-menu-container"
                                                    ref={
                                                        menuAberto
                                                        === conversa.id_conversa

                                                            ? menuRef

                                                            : null
                                                    }
                                                >

                                                    <span
                                                        className="conversation-more"
                                                        onClick={
                                                            (event) =>
                                                                alternarMenu(
                                                                    event,
                                                                    conversa.id_conversa
                                                                )
                                                        }
                                                    >

                                                        <MoreHorizontal
                                                            size={18}
                                                        />

                                                    </span>


                                                    {
                                                        menuAberto
                                                        === conversa.id_conversa
                                                        && (

                                                            <span
                                                                className="conversation-menu"
                                                            >

                                                                <span
                                                                    onClick={
                                                                        (event) =>
                                                                            iniciarRenomeacao(
                                                                                event,
                                                                                conversa
                                                                            )
                                                                    }
                                                                >

                                                                    <Pencil
                                                                        size={15}
                                                                    />

                                                                    Renomear

                                                                </span>


                                                                <span
                                                                    onClick={
                                                                        (event) =>
                                                                            arquivarConversa(
                                                                                event,
                                                                                conversa
                                                                            )
                                                                    }
                                                                >

                                                                    <Archive
                                                                        size={15}
                                                                    />

                                                                    Arquivar

                                                                </span>


                                                                <span
                                                                    className="danger"
                                                                    onClick={
                                                                        (event) =>
                                                                            excluirConversa(
                                                                                event,
                                                                                conversa
                                                                            )
                                                                    }
                                                                >

                                                                    <Trash2
                                                                        size={15}
                                                                    />

                                                                    Excluir

                                                                </span>

                                                            </span>

                                                        )
                                                    }

                                                </span>

                                            </button>

                                        )
                                }

                            </div>

                        )
                    )
                }

            </div>


            {/* ==================================================
                CONVERSAS ARQUIVADAS
            ================================================== */}

            <div className="archived-section">

                <button
                    className="archived-button"
                    onClick={alternarArquivadas}
                >

                    <Archive size={17} />

                    <span>
                        Conversas arquivadas
                    </span>

                </button>


                {
                    mostrarArquivadas
                    && (
                        <div className="archived-list">

                            {
                                conversasArquivadas.length === 0
                                    ? (

                                        <div className="no-conversations">

                                            Nenhuma conversa arquivada.

                                        </div>

                                    )
                                    : (

                                        conversasArquivadas.map(
                                            (conversa) => (

                                                <div
                                                    key={conversa.id_conversa}
                                                    className="archived-item"
                                                >

                                                    <span
                                                        title={conversa.titulo}
                                                    >

                                                        {conversa.titulo}

                                                    </span>


                                                    <button
                                                        onClick={
                                                            () =>
                                                                restaurarConversa(
                                                                    conversa
                                                                )
                                                        }
                                                        title="Restaurar conversa"
                                                    >

                                                        <RotateCcw
                                                            size={14}
                                                        />

                                                        Restaurar

                                                    </button>

                                                </div>

                                            )
                                        )

                                    )
                            }

                        </div>
                    )
                }

            </div>


            {/* ==================================================
                RODAPÉ
            ================================================== */}

            <div className="sidebar-footer">

                <button>

                    <Settings size={18} />

                    <span>
                        Configurações
                    </span>

                </button>


                <button
                    onClick={logout}
                >

                    <User size={18} />

                    <span>
                        Sair
                        {
                            usuario?.nome
                                ? ` (${usuario.nome})`
                                : ""
                        }
                    </span>

                </button>

            </div>

        </aside>
    );
}


export default Sidebar;