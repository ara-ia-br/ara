import { useEffect, useMemo, useState } from "react";
import { Archive, ArrowUpRight, Check, FolderKanban, FolderPlus, MessageSquare, RotateCcw, Search, Trash2, Share2, Pencil, X } from "lucide-react";
import { useNavigate, useOutletContext } from "react-router-dom";
import api from "../services/api";
import { useAuth } from "../context/AuthContext";

function formatDate(value) {
    if (!value) return "";
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return "";
    return new Intl.DateTimeFormat("pt-BR", { day: "2-digit", month: "short" }).format(date).replace(".", "");
}

function ConversationsPage() {
    const { usuario } = useAuth();
    const navigate = useNavigate();
    const { conversaSelecionada, setConversaSelecionada, conversaCriada } = useOutletContext();
    const [conversas, setConversas] = useState([]);
    const [busca, setBusca] = useState("");
    const [filtro, setFiltro] = useState("TODAS");
    const [carregando, setCarregando] = useState(true);
    const [projetos, setProjetos] = useState([]);
    const [projetoAberto, setProjetoAberto] = useState(null);
    const [adicionandoProjeto, setAdicionandoProjeto] = useState(null);
    const [renomeando, setRenomeando] = useState(null);
    const [novoTitulo, setNovoTitulo] = useState("");
    const [salvandoTitulo, setSalvandoTitulo] = useState(false);
    const [criandoProjetoPara, setCriandoProjetoPara] = useState(null);
    const [nomeProjeto, setNomeProjeto] = useState("");
    const [descricaoProjeto, setDescricaoProjeto] = useState("");
    const [salvandoProjeto, setSalvandoProjeto] = useState(false);

    async function carregar() {
        if (!usuario?.id_usuario) return;
        setCarregando(true);
        try {
            const resposta = await api.get(`/conversas/usuario/${usuario.id_usuario}/todas`);
            setConversas(Array.isArray(resposta.data) ? resposta.data : []);
        } catch (erro) {
            console.error("Erro ao carregar conversas:", erro);
        } finally {
            setCarregando(false);
        }
    }

    async function carregarProjetos() {
        if (!usuario?.id_usuario) return;
        try {
            const resposta = await api.get(`/projetos/usuario/${usuario.id_usuario}`);
            setProjetos(Array.isArray(resposta.data) ? resposta.data : []);
        } catch (erro) {
            console.error("Erro ao carregar projetos:", erro);
        }
    }

    useEffect(() => {
        carregar();
        carregarProjetos();
    }, [usuario?.id_usuario]);

    const filtradas = useMemo(() => {
        const termo = busca.trim().toLowerCase();
        return conversas.filter((conversa) => {
            const combinaFiltro = filtro === "TODAS" || (filtro === "ARQUIVADAS" ? conversa.status === "ARQUIVADA" : conversa.status !== "ARQUIVADA");
            const combinaBusca = !termo || conversa.titulo.toLowerCase().includes(termo);
            return combinaFiltro && combinaBusca;
        });
    }, [conversas, busca, filtro]);

    async function restaurar(conversa) {
        try {
            const resposta = await api.patch(`/conversas/${conversa.id_conversa}/restaurar`);
            setConversas((lista) => lista.map((item) => item.id_conversa === conversa.id_conversa ? resposta.data : item));
            conversaCriada();
        } catch (erro) {
            console.error("Erro ao restaurar:", erro);
        }
    }

    async function arquivar(conversa) {
        try {
            const resposta = await api.patch(`/conversas/${conversa.id_conversa}/arquivar`);
            setConversas((lista) => lista.map((item) => item.id_conversa === conversa.id_conversa ? resposta.data : item));
            conversaCriada();
        } catch (erro) {
            console.error("Erro ao arquivar:", erro);
        }
    }

    async function excluir(conversa) {
        if (!window.confirm(`Excluir definitivamente “${conversa.titulo}”?`)) return;
        try {
            await api.delete(`/conversas/${conversa.id_conversa}`);
            setConversas((lista) => lista.filter((item) => item.id_conversa !== conversa.id_conversa));
            conversaCriada();
        } catch (erro) {
            console.error("Erro ao excluir:", erro);
        }
    }

    function abrirConversa(conversa) {
        setConversaSelecionada(conversa);
        navigate("/chat");
    }
    function iniciarRenomeacao(conversa) {
        setProjetoAberto(null);
        setRenomeando(conversa.id_conversa);
        setNovoTitulo(conversa.titulo || "");
    }

    function cancelarRenomeacao() {
        setRenomeando(null);
        setNovoTitulo("");
    }

    async function salvarNovoTitulo(event, conversa) {
        event.preventDefault();
        const titulo = novoTitulo.trim();
        if (!titulo || salvandoTitulo) return;

        setSalvandoTitulo(true);
        try {
            const resposta = await api.patch(`/conversas/${conversa.id_conversa}/titulo`, { titulo });
            setConversas((lista) => lista.map((item) =>
                item.id_conversa === conversa.id_conversa ? resposta.data : item
            ));
            if (conversaSelecionada?.id_conversa === conversa.id_conversa) {
                setConversaSelecionada(resposta.data);
            }
            conversaCriada();
            cancelarRenomeacao();
        } catch (erro) {
            console.error("Erro ao renomear conversa:", erro);
        } finally {
            setSalvandoTitulo(false);
        }
    }

    function compartilharConversa(conversa) {
        const texto = `Conversa: ${conversa.titulo}`;

        if (navigator.share) {
            navigator.share({
                title: conversa.titulo,
                text: texto
            }).catch(() => {});
            return;
        }

        if (navigator.clipboard) {
            navigator.clipboard.writeText(texto).then(() => {
                window.alert("Informações da conversa copiadas para a área de transferência.");
            }).catch((erro) => {
                console.error("Erro ao copiar conversa:", erro);
            });
        }
    }

    async function adicionarAoProjeto(conversa, projeto) {
        setAdicionandoProjeto(conversa.id_conversa);
        try {
            const resposta = await api.patch(`/projetos/${projeto.id_projeto}/conversas/${conversa.id_conversa}`);
            setConversas((lista) => lista.map((item) =>
                item.id_conversa === conversa.id_conversa
                    ? { ...item, ...resposta.data, id_projeto: projeto.id_projeto }
                    : item
            ));
            setProjetoAberto(null);
            conversaCriada();
        } catch (erro) {
            console.error("Erro ao adicionar conversa ao projeto:", erro);
        } finally {
            setAdicionandoProjeto(null);
        }
    }

    function abrirCriacaoProjeto(conversa) {
        setProjetoAberto(null);
        setCriandoProjetoPara(conversa);
        setNomeProjeto("");
        setDescricaoProjeto("");
    }

    function fecharCriacaoProjeto(forcar = false) {
        if (salvandoProjeto && !forcar) return;
        setCriandoProjetoPara(null);
        setNomeProjeto("");
        setDescricaoProjeto("");
    }

    async function criarProjetoParaConversa(event) {
        event.preventDefault();
        const nome = nomeProjeto.trim();
        if (!nome || !criandoProjetoPara || salvandoProjeto) return;

        setSalvandoProjeto(true);
        try {
            const projetoResposta = await api.post("/projetos", {
                id_usuario: usuario.id_usuario,
                nome,
                descricao: descricaoProjeto.trim()
            });
            const projeto = projetoResposta.data;

            setProjetos((lista) => [projeto, ...lista]);

            const conversaResposta = await api.patch(
                `/projetos/${projeto.id_projeto}/conversas/${criandoProjetoPara.id_conversa}`
            );

            setConversas((lista) => lista.map((item) =>
                item.id_conversa === criandoProjetoPara.id_conversa
                    ? { ...item, ...conversaResposta.data, id_projeto: projeto.id_projeto }
                    : item
            ));

            if (conversaSelecionada?.id_conversa === criandoProjetoPara.id_conversa) {
                setConversaSelecionada((atual) => atual ? { ...atual, ...conversaResposta.data, id_projeto: projeto.id_projeto } : atual);
            }

            fecharCriacaoProjeto(true);
            conversaCriada();
        } catch (erro) {
            console.error("Erro ao criar projeto:", erro);
        } finally {
            setSalvandoProjeto(false);
        }
    }


    const totalArquivadas = conversas.filter((item) => item.status === "ARQUIVADA").length;
    const totalAtivas = conversas.filter((item) => item.status !== "ARQUIVADA").length;

    return (
        <main className="ara-page conversations-page">
            <header className="conversations-hero">
                <div>
                    <span className="page-kicker">HISTÓRICO</span>
                    <h1>Conversas</h1>
                    <p>Encontre, abra e organize suas conversas sem precisar procurar na barra lateral.</p>
                </div>
                <button className="conversations-refresh" onClick={carregar} title="Atualizar lista">
                    <RotateCcw size={17} /> Atualizar
                </button>
            </header>

            <section className="conversation-library panel">
                <div className="conversation-library-top">
                    <div className="conversation-search">
                        <Search size={19} />
                        <input value={busca} onChange={(event) => setBusca(event.target.value)} placeholder="Pesquisar conversas" />
                    </div>
                    <div className="conversation-stats">
                        <span><strong>{conversas.length}</strong> total</span>
                        <span><strong>{totalAtivas}</strong> ativas</span>
                        <span><strong>{totalArquivadas}</strong> arquivadas</span>
                    </div>
                </div>

                <div className="conversation-tabs">
                    <button className={filtro === "ARQUIVADAS" ? "active" : ""} onClick={() => setFiltro("ARQUIVADAS")}><Archive size={16} /> Arquivadas</button>
                    <button className={filtro === "TODAS" ? "active" : ""} onClick={() => setFiltro("TODAS")}><MessageSquare size={16} /> Todas</button>
                    <button className={filtro === "ATIVAS" ? "active" : ""} onClick={() => setFiltro("ATIVAS")}><Check size={16} /> Ativas</button>
                </div>

                <div className="conversation-library-list">
                    {carregando ? (
                        <div className="library-empty">Carregando conversas...</div>
                    ) : filtradas.length === 0 ? (
                        <div className="library-empty">
                            <Archive size={30} />
                            <strong>Nenhuma conversa encontrada</strong>
                            <span>{busca ? "Tente outro termo de pesquisa." : "Ainda não há conversas para exibir."}</span>
                        </div>
                    ) : filtradas.map((conversa) => (
                        <article className="library-conversation" key={conversa.id_conversa}>
                            {renomeando === conversa.id_conversa ? (
                                <form className="library-conversation-rename" onSubmit={(event) => salvarNovoTitulo(event, conversa)}>
                                    <span className="library-conversation-icon"><MessageSquare size={19} /></span>
                                    <input
                                        value={novoTitulo}
                                        onChange={(event) => setNovoTitulo(event.target.value)}
                                        onKeyDown={(event) => {
                                            if (event.key === "Escape") cancelarRenomeacao();
                                        }}
                                        maxLength={200}
                                        autoFocus
                                        aria-label="Novo nome da conversa"
                                    />
                                    <button type="submit" title="Salvar nome" disabled={salvandoTitulo || !novoTitulo.trim()}>
                                        <Check size={16} />
                                    </button>
                                    <button type="button" title="Cancelar" onClick={cancelarRenomeacao} disabled={salvandoTitulo}>
                                        <X size={16} />
                                    </button>
                                </form>
                            ) : (
                                <button className="library-conversation-main" onClick={() => abrirConversa(conversa)}>
                                    <span className="library-conversation-icon"><MessageSquare size={19} /></span>
                                    <span className="library-conversation-copy">
                                        <strong>{conversa.titulo}</strong>
                                        <small>
                                            {conversa.status === "ARQUIVADA" ? "Arquivada" : "Ativa"} · {formatDate(conversa.data_atualizacao)}
                                            {conversa.id_projeto ? " · Em um projeto" : ""}
                                        </small>
                                    </span>
                                </button>
                            )}

                            <div className="library-conversation-actions">
                                {conversa.id_projeto && <span className="conversation-project-badge"><FolderKanban size={14} /> Projeto</span>}

                                <div className="conversation-project-action">
                                    <button
                                        className={projetoAberto === conversa.id_conversa ? "project-action-button active" : "project-action-button"}
                                        title={conversa.id_projeto ? "Alterar projeto" : "Adicionar a projeto"}
                                        onClick={() => setProjetoAberto((atual) => atual === conversa.id_conversa ? null : conversa.id_conversa)}
                                    >
                                        <FolderKanban size={17} />
                                    </button>

                                    {projetoAberto === conversa.id_conversa && (
                                        <div className="conversation-project-popover">
                                            <div className="conversation-project-popover-header">
                                                <div>
                                                    <strong>{conversa.id_projeto ? "Alterar projeto" : "Adicionar a projeto"}</strong>
                                                    <small>Escolha onde esta conversa ficará.</small>
                                                </div>
                                                <button type="button" onClick={() => setProjetoAberto(null)} title="Fechar"><X size={15} /></button>
                                            </div>

                                            {projetos.length === 0 ? (
                                                <div className="conversation-project-empty">
                                                    <FolderKanban size={22} />
                                                    <span>Você ainda não criou nenhum projeto.</span>
                                                    <button type="button" onClick={() => abrirCriacaoProjeto(conversa)}>Criar projeto</button>
                                                </div>
                                            ) : (
                                                <>
                                                    <button
                                                        type="button"
                                                        className="conversation-create-project-button"
                                                        onClick={() => abrirCriacaoProjeto(conversa)}
                                                    >
                                                        <span className="conversation-project-option-icon"><FolderPlus size={15} /></span>
                                                        <span><strong>Criar novo projeto</strong><small>Crie e adicione esta conversa</small></span>
                                                    </button>
                                                    <div className="conversation-project-options">
                                                    {projetos.map((projeto) => (
                                                        <button
                                                            type="button"
                                                            key={projeto.id_projeto}
                                                            className={conversa.id_projeto === projeto.id_projeto ? "selected" : ""}
                                                            disabled={adicionandoProjeto === conversa.id_conversa}
                                                            onClick={() => adicionarAoProjeto(conversa, projeto)}
                                                        >
                                                            <span className="conversation-project-option-icon"><FolderKanban size={15} /></span>
                                                            <span><strong>{projeto.nome}</strong><small>{projeto.descricao || "Projeto"}</small></span>
                                                            {conversa.id_projeto === projeto.id_projeto && <Check size={15} />}
                                                        </button>
                                                    ))}
                                                    </div>
                                                </>
                                            )}
                                        </div>
                                    )}
                                </div>

                                <button title="Compartilhar" onClick={() => compartilharConversa(conversa)}><Share2 size={17} /></button>
                                <button title="Renomear" onClick={() => iniciarRenomeacao(conversa)}><Pencil size={17} /></button>
                                <button title="Abrir" onClick={() => abrirConversa(conversa)}><ArrowUpRight size={17} /></button>
                                {conversa.status === "ARQUIVADA" ? (
                                    <button title="Restaurar" onClick={() => restaurar(conversa)}><RotateCcw size={17} /></button>
                                ) : (
                                    <button title="Arquivar" onClick={() => arquivar(conversa)}><Archive size={17} /></button>
                                )}
                                <button className="danger" title="Excluir" onClick={() => excluir(conversa)}><Trash2 size={17} /></button>
                            </div>
                        </article>
                    ))}
                </div>
            </section>

            {criandoProjetoPara && (
                <div
                    className="conversation-project-modal-backdrop"
                    onMouseDown={(event) => event.target === event.currentTarget && fecharCriacaoProjeto()}
                >
                    <form className="conversation-project-modal" onSubmit={criarProjetoParaConversa}>
                        <div className="conversation-project-modal-header">
                            <div>
                                <span className="page-kicker">NOVO PROJETO</span>
                                <h2>Criar projeto</h2>
                                <p>O projeto será criado e esta conversa será adicionada a ele.</p>
                            </div>
                            <button type="button" onClick={fecharCriacaoProjeto} title="Fechar"><X size={18} /></button>
                        </div>

                        <label>
                            Nome
                            <input
                                autoFocus
                                value={nomeProjeto}
                                onChange={(event) => setNomeProjeto(event.target.value)}
                                maxLength={120}
                                placeholder="Ex.: Projeto A.R.A."
                            />
                        </label>

                        <label>
                            Descrição <span>opcional</span>
                            <textarea
                                value={descricaoProjeto}
                                onChange={(event) => setDescricaoProjeto(event.target.value)}
                                maxLength={5000}
                                rows={4}
                                placeholder="Descreva o objetivo deste projeto..."
                            />
                        </label>

                        <div className="conversation-project-modal-actions">
                            <button type="button" className="secondary" onClick={fecharCriacaoProjeto} disabled={salvandoProjeto}>Cancelar</button>
                            <button type="submit" className="primary" disabled={salvandoProjeto || !nomeProjeto.trim()}>
                                {salvandoProjeto ? "Criando..." : "Criar projeto"}
                            </button>
                        </div>
                    </form>
                </div>
            )}
        </main>
    );
}

export default ConversationsPage;