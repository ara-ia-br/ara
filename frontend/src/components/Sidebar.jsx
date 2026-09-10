import { useEffect, useMemo, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import {
    Archive,
    Bot,
    CalendarDays,
    ChevronLeft,
    ChevronRight,
    FileText,
    FolderKanban,
    History,
    Home,
    ListTodo,
    MemoryStick,
    MessageSquare,
    MessageSquarePlus,
    MoreHorizontal,
    Pencil,
    Plug,
    RotateCcw,
    Search,
    Settings,
    Trash2,
    Workflow
} from "lucide-react";
import api from "../services/api";
import { useAuth } from "../context/AuthContext";
import BrandMark from "./BrandMark";

const navItems = [
    { label: "Hoje", path: "/hoje", icon: Home },
    { label: "A.R.A.", path: "/chat", icon: Bot },
    { label: "Tarefas", path: "/tarefas", icon: ListTodo },
    { label: "Agenda", path: "/agenda", icon: CalendarDays },
    { label: "Memória", path: "/memoria", icon: MemoryStick },
    { label: "Arquivos", path: "/arquivos", icon: FileText },
    { label: "Projetos", path: "/projetos", icon: FolderKanban },
    { label: "Automações", path: "/automacoes", icon: Workflow },
    { label: "Integrações", path: "/integracoes", icon: Plug }
];

function Sidebar({
    conversaSelecionada,
    setConversaSelecionada,
    atualizarConversas,
    conversaCriada,
    recolhida,
    setRecolhida,
    onOpenCommand
}) {
    const { usuario, logout } = useAuth();
    const navigate = useNavigate();
    const location = useLocation();
    const [conversas, setConversas] = useState([]);
    const [arquivadas, setArquivadas] = useState([]);
    const [mostrarArquivadas, setMostrarArquivadas] = useState(false);
    const [criando, setCriando] = useState(false);
    const [menuAberto, setMenuAberto] = useState(null);
    const [renomeando, setRenomeando] = useState(null);
    const [novoTitulo, setNovoTitulo] = useState("");

    async function carregarConversas() {
        if (!usuario?.id_usuario) return;
        try {
            const resposta = await api.get(`/conversas/usuario/${usuario.id_usuario}`);
            const lista = Array.isArray(resposta.data) ? resposta.data : [];
            setConversas(lista);
            if (!conversaSelecionada && lista.length > 0) setConversaSelecionada(lista[0]);
            if (conversaSelecionada) {
                const atualizada = lista.find((item) => item.id_conversa === conversaSelecionada.id_conversa);
                if (atualizada) setConversaSelecionada(atualizada);
            }
        } catch (erro) {
            console.error("Erro ao carregar conversas:", erro);
        }
    }

    async function carregarArquivadas() {
        if (!usuario?.id_usuario) return;
        try {
            const resposta = await api.get(`/conversas/usuario/${usuario.id_usuario}/arquivadas`);
            setArquivadas(Array.isArray(resposta.data) ? resposta.data : []);
        } catch (erro) {
            console.error("Erro ao carregar conversas arquivadas:", erro);
        }
    }

    useEffect(() => { carregarConversas(); }, [usuario?.id_usuario, atualizarConversas]);
    useEffect(() => { if (mostrarArquivadas) carregarArquivadas(); }, [mostrarArquivadas]);

    async function criarNovaConversa() {
        if (criando || !usuario?.id_usuario) return;
        setCriando(true);
        try {
            const resposta = await api.post("/conversas", {
                id_usuario: usuario.id_usuario,
                titulo: "Nova conversa"
            });
            setConversaSelecionada(resposta.data);
            conversaCriada();
            navigate("/chat");
        } catch (erro) {
            console.error("Erro ao criar conversa:", erro);
        } finally {
            setCriando(false);
        }
    }

    function iniciarRenomeacao(conversa) {
        setRenomeando(conversa.id_conversa);
        setNovoTitulo(conversa.titulo || "");
        setMenuAberto(null);
    }

    async function salvarNovoTitulo(event, conversa) {
        event.preventDefault();
        const titulo = novoTitulo.trim();
        if (!titulo) return;
        try {
            const resposta = await api.patch(`/conversas/${conversa.id_conversa}/titulo`, { titulo });
            setConversas((anteriores) => anteriores.map((item) => item.id_conversa === conversa.id_conversa ? resposta.data : item));
            if (conversaSelecionada?.id_conversa === conversa.id_conversa) setConversaSelecionada(resposta.data);
            setRenomeando(null);
        } catch (erro) {
            console.error("Erro ao renomear conversa:", erro);
        }
    }

    async function arquivarConversa(conversa) {
        if (!window.confirm(`Arquivar “${conversa.titulo}”?`)) return;
        try {
            await api.patch(`/conversas/${conversa.id_conversa}/arquivar`);
            setConversas((anteriores) => anteriores.filter((item) => item.id_conversa !== conversa.id_conversa));
            if (conversaSelecionada?.id_conversa === conversa.id_conversa) setConversaSelecionada(null);
            conversaCriada();
            setMenuAberto(null);
        } catch (erro) {
            console.error("Erro ao arquivar conversa:", erro);
        }
    }

    async function restaurarConversa(conversa) {
        try {
            const resposta = await api.patch(`/conversas/${conversa.id_conversa}/restaurar`);
            setArquivadas((anteriores) => anteriores.filter((item) => item.id_conversa !== conversa.id_conversa));
            conversaCriada();
            setConversaSelecionada(resposta.data);
            navigate("/chat");
        } catch (erro) {
            console.error("Erro ao restaurar conversa:", erro);
        }
    }

    async function excluirConversa(conversa) {
        if (!window.confirm(`Excluir definitivamente “${conversa.titulo}”?`)) return;
        try {
            await api.delete(`/conversas/${conversa.id_conversa}`);
            setConversas((anteriores) => anteriores.filter((item) => item.id_conversa !== conversa.id_conversa));
            if (conversaSelecionada?.id_conversa === conversa.id_conversa) setConversaSelecionada(null);
            conversaCriada();
            setMenuAberto(null);
        } catch (erro) {
            console.error("Erro ao excluir conversa:", erro);
        }
    }

    const iniciais = useMemo(() => {
        const nome = usuario?.nome || usuario?.email || "U";
        return nome.split(/\s+/).slice(0, 2).map((parte) => parte[0]?.toUpperCase()).join("");
    }, [usuario]);

    return (
        <aside className={recolhida ? "sidebar ara-sidebar collapsed" : "sidebar ara-sidebar"}>
            <div className="sidebar-topline">
                <BrandMark compact={recolhida} />
                <button className="sidebar-collapse" onClick={() => setRecolhida(!recolhida)} aria-label="Recolher menu">
                    {recolhida ? <ChevronRight size={17} /> : <ChevronLeft size={17} />}
                </button>
            </div>

            <button className="new-chat ara-new-chat" onClick={criarNovaConversa} disabled={criando} title="Nova conversa">
                <MessageSquarePlus size={18} /><span>{criando ? "Criando..." : "Nova conversa"}</span>
            </button>

            <button className="command-trigger" onClick={onOpenCommand} title="Command Center">
                <Search size={17} /><span>Command Center</span><kbd>Ctrl K</kbd>
            </button>

            <nav className="ara-nav" aria-label="Principal">
                {navItems.map(({ label, path, icon: Icon }) => (
                    <button
                        key={path}
                        className={location.pathname === path ? "ara-nav-item active" : "ara-nav-item"}
                        onClick={() => navigate(path)}
                        title={label}
                    >
                        <Icon size={18} /><span>{label}</span>
                    </button>
                ))}
            </nav>

            {!recolhida && (
                <section className="conversation-section">
                    <div className="sidebar-section-heading">
                        <span>CONVERSAS RECENTES</span>
                        <button onClick={() => setMostrarArquivadas(!mostrarArquivadas)} title="Arquivadas"><History size={15} /></button>
                    </div>

                    <div className="conversation-list">
                        {conversas.slice(0, 12).map((conversa) => (
                            <div className="conversation-row" key={conversa.id_conversa}>
                                {renomeando === conversa.id_conversa ? (
                                    <form className="conversation-rename" onSubmit={(event) => salvarNovoTitulo(event, conversa)}>
                                        <input value={novoTitulo} onChange={(event) => setNovoTitulo(event.target.value)} autoFocus maxLength={200} />
                                    </form>
                                ) : (
                                    <button
                                        className={conversaSelecionada?.id_conversa === conversa.id_conversa ? "conversation-link active" : "conversation-link"}
                                        onClick={() => { setConversaSelecionada(conversa); navigate("/chat"); }}
                                    >
                                        <MessageSquare size={15} /><span>{conversa.titulo}</span>
                                    </button>
                                )}
                                <button className="conversation-more" onClick={() => setMenuAberto(menuAberto === conversa.id_conversa ? null : conversa.id_conversa)}>
                                    <MoreHorizontal size={16} />
                                </button>
                                {menuAberto === conversa.id_conversa && (
                                    <div className="conversation-popover">
                                        <button onClick={() => iniciarRenomeacao(conversa)}><Pencil size={14} /> Renomear</button>
                                        <button onClick={() => arquivarConversa(conversa)}><Archive size={14} /> Arquivar</button>
                                        <button className="danger" onClick={() => excluirConversa(conversa)}><Trash2 size={14} /> Excluir</button>
                                    </div>
                                )}
                            </div>
                        ))}
                        {conversas.length === 0 && <p className="sidebar-empty">Nenhuma conversa ainda.</p>}
                    </div>

                    {mostrarArquivadas && (
                        <div className="archived-block">
                            <span>ARQUIVADAS</span>
                            {arquivadas.map((conversa) => (
                                <button key={conversa.id_conversa} onClick={() => restaurarConversa(conversa)}>
                                    <RotateCcw size={14} /><span>{conversa.titulo}</span>
                                </button>
                            ))}
                            {arquivadas.length === 0 && <small>Nenhuma conversa arquivada.</small>}
                        </div>
                    )}
                </section>
            )}

            <div className="sidebar-footer">
                <button className={location.pathname === "/configuracoes" ? "profile-card active" : "profile-card"} onClick={() => navigate("/configuracoes")}>
                    <span className="profile-avatar">{iniciais}</span>
                    <span className="profile-copy"><strong>{usuario?.nome || "Minha conta"}</strong><small>{usuario?.email || "Configurações"}</small></span>
                    <Settings size={16} />
                </button>
                {!recolhida && <button className="logout-link" onClick={logout}>Sair da sessão</button>}
            </div>
        </aside>
    );
}

export default Sidebar;
