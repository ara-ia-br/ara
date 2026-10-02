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
    FolderPlus,
    Home,
    Link2,
    ListTodo,
    MemoryStick,
    MessageSquare,
    MessageSquarePlus,
    MoreVertical,
    Pencil,
    Plug,
    RotateCw,
    Search,
    Settings,
    Trash2,
    Workflow,
    Share2
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
    const [projetos, setProjetos] = useState([]);
    const [criando, setCriando] = useState(false);
    const [menuAberto, setMenuAberto] = useState(null);
    const [menuPos, setMenuPos] = useState(null);
    const [renomeando, setRenomeando] = useState(null);
    const [novoTitulo, setNovoTitulo] = useState("");
    const [projetoAberto, setProjetoAberto] = useState(null);

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

    async function carregarProjetos() {
        if (!usuario?.id_usuario) return;
        try {
            const resposta = await api.get(`/projetos/usuario/${usuario.id_usuario}`);
            setProjetos(Array.isArray(resposta.data) ? resposta.data : []);
        } catch (erro) {
            // O backend pode ainda não ter sido reiniciado com o módulo de projetos.
            console.error("Erro ao carregar projetos:", erro);
        }
    }

    useEffect(() => { carregarConversas(); }, [usuario?.id_usuario, atualizarConversas]);
    useEffect(() => { carregarProjetos(); }, [usuario?.id_usuario, atualizarConversas]);

    function recarregarListaAtual() {
        carregarConversas();
        carregarProjetos();
    }

    useEffect(() => {
        if (!menuAberto) return;
        function fecharAoRolar() {
            setMenuAberto(null);
            setMenuPos(null);
            setProjetoAberto(null);
        }
        window.addEventListener("scroll", fecharAoRolar, true);
        window.addEventListener("resize", fecharAoRolar);
        return () => {
            window.removeEventListener("scroll", fecharAoRolar, true);
            window.removeEventListener("resize", fecharAoRolar);
        };
    }, [menuAberto]);

    useEffect(() => {
        if (!menuAberto) return;
        function fecharAoClicarFora(event) {
            if (event.target.closest(".conversation-popover") || event.target.closest(".conversation-more")) return;
            setMenuAberto(null);
            setMenuPos(null);
            setProjetoAberto(null);
        }
        document.addEventListener("mousedown", fecharAoClicarFora);
        return () => document.removeEventListener("mousedown", fecharAoClicarFora);
    }, [menuAberto]);

    function alternarMenu(event, conversa) {
        const jaAberto = menuAberto === conversa.id_conversa;
        if (jaAberto) {
            setMenuAberto(null);
            setMenuPos(null);
            setProjetoAberto(null);
            return;
        }
        const rect = event.currentTarget.getBoundingClientRect();
        setMenuPos({
            top: Math.min(rect.bottom + 7, window.innerHeight - 310),
            right: Math.max(12, window.innerWidth - rect.right)
        });
        setMenuAberto(conversa.id_conversa);
        setProjetoAberto(null);
    }

    function fecharMenu() {
        setMenuAberto(null);
        setMenuPos(null);
        setProjetoAberto(null);
    }

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
        fecharMenu();
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
            fecharMenu();
        } catch (erro) {
            console.error("Erro ao arquivar conversa:", erro);
        }
    }

    async function excluirConversa(conversa) {
        if (!window.confirm(`Excluir definitivamente “${conversa.titulo}”?`)) return;
        try {
            await api.delete(`/conversas/${conversa.id_conversa}`);
            setConversas((anteriores) => anteriores.filter((item) => item.id_conversa !== conversa.id_conversa));
            if (conversaSelecionada?.id_conversa === conversa.id_conversa) setConversaSelecionada(null);
            conversaCriada();
            fecharMenu();
        } catch (erro) {
            console.error("Erro ao excluir conversa:", erro);
        }
    }

    function compartilharConversa(conversa) {
        const texto = `Conversa: ${conversa.titulo}`;
        if (navigator.share) {
            navigator.share({ title: conversa.titulo, text: texto }).catch(() => {});
        } else if (navigator.clipboard) {
            navigator.clipboard.writeText(texto);
        }
        fecharMenu();
    }

    async function colocarEmProjeto(conversa, projeto) {
        try {
            const resposta = await api.patch(`/projetos/${projeto.id_projeto}/conversas/${conversa.id_conversa}`);
            setConversas((anteriores) => anteriores.map((item) => item.id_conversa === conversa.id_conversa ? resposta.data : item));
            if (conversaSelecionada?.id_conversa === conversa.id_conversa) setConversaSelecionada(resposta.data);
            conversaCriada();
            fecharMenu();
        } catch (erro) {
            console.error("Erro ao colocar conversa no projeto:", erro);
        }
    }

    const iniciais = useMemo(() => {
        const nome = usuario?.nome || usuario?.email || "U";
        return nome.split(/\s+/).slice(0, 2).map((parte) => parte[0]?.toUpperCase()).join("");
    }, [usuario]);

    const listaExibida = conversas.slice(0, 12);

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

            <nav className="ara-nav">
                {navItems.map((item) => {
                    const Icon = item.icon;
                    const ativo = location.pathname === item.path || (item.path === "/projetos" && location.pathname.startsWith("/projetos"));
                    return (
                        <button key={item.path} className={ativo ? "ara-nav-item active" : "ara-nav-item"} onClick={() => navigate(item.path)}>
                            <Icon size={18} /><span>{item.label}</span>
                        </button>
                    );
                })}

                <button
                    className={(location.pathname.startsWith("/conversas") || location.pathname.startsWith("/arquivadas")) ? "ara-nav-item active" : "ara-nav-item"}
                    onClick={() => navigate("/conversas")}
                    title="Abrir todas as conversas"
                >
                    <MessageSquare size={18} /><span>Conversas</span>
                </button>
            </nav>

            {!recolhida && (
                <section className="conversation-section">
                    <div className="sidebar-section-heading">
                        <span>CONVERSAS RECENTES</span>
                        <button onClick={recarregarListaAtual} title="Recarregar">
                            <RotateCw size={14} />
                        </button>
                    </div>

                    <div className="conversation-list">
                        {listaExibida.map((conversa) => (
                            <div className="conversation-row" key={conversa.id_conversa}>
                                {renomeando === conversa.id_conversa ? (
                                    <form className="conversation-rename" onSubmit={(event) => salvarNovoTitulo(event, conversa)}>
                                        <input value={novoTitulo} onChange={(event) => setNovoTitulo(event.target.value)} autoFocus maxLength={200} onBlur={() => setRenomeando(null)} />
                                    </form>
                                ) : (
                                    <button
                                        className={conversaSelecionada?.id_conversa === conversa.id_conversa ? "conversation-link active" : "conversation-link"}
                                        onClick={() => { setConversaSelecionada(conversa); navigate("/chat"); }}
                                    >
                                        <MessageSquare size={15} /><span>{conversa.titulo}</span>
                                    </button>
                                )}

                                <button className="conversation-more" onClick={(event) => alternarMenu(event, conversa)} aria-label={`Mais opções para ${conversa.titulo}`}>
                                    <MoreVertical size={17} />
                                </button>

                                {menuAberto === conversa.id_conversa && menuPos && (
                                    <div className="conversation-popover" style={{ top: menuPos.top, right: menuPos.right }}>
                                        <div className="popover-heading">AÇÕES DA CONVERSA</div>
                                        <button onClick={() => iniciarRenomeacao(conversa)}><Pencil size={15} /> Renomear</button>
                                        <button className="project-action" onClick={() => setProjetoAberto((valor) => valor ? null : conversa.id_conversa)}>
                                            <FolderPlus size={15} /> <span>Adicionar a projeto</span><ChevronRight size={14} className={projetoAberto ? "popover-chevron open" : "popover-chevron"} />
                                        </button>

                                        {projetoAberto === conversa.id_conversa && (
                                            <div className="project-picker">
                                                <div className="project-picker-title">SELECIONE UM PROJETO</div>
                                                {projetos.length > 0 ? projetos.map((projeto) => (
                                                    <button key={projeto.id_projeto} onClick={() => colocarEmProjeto(conversa, projeto)}>
                                                        <FolderKanban size={14} />
                                                        <span>{projeto.nome}</span>
                                                    </button>
                                                )) : (
                                                    <div className="project-picker-empty">Nenhum projeto criado.</div>
                                                )}
                                                <button className="new-project-option" onClick={() => { fecharMenu(); navigate("/projetos?novo=1"); }}>
                                                    <FolderPlus size={14} /> Criar novo projeto
                                                </button>
                                            </div>
                                        )}

                                        <div className="popover-divider" />
                                        <button onClick={() => compartilharConversa(conversa)}><Share2 size={15} /> Compartilhar</button>
                                        <button onClick={() => arquivarConversa(conversa)}><Archive size={15} /> Arquivar</button>
                                        <button className="danger" onClick={() => excluirConversa(conversa)}><Trash2 size={15} /> Excluir</button>
                                    </div>
                                )}
                            </div>
                        ))}

                        {listaExibida.length === 0 && (
                            <p className="sidebar-empty">Nenhuma conversa ainda.</p>
                        )}
                    </div>
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
