import { useEffect, useMemo, useState } from "react";
import { Archive, Check, Edit3, FolderKanban, FolderPlus, MessageSquare, Plus, Search, Trash2, X } from "lucide-react";
import { useLocation, useOutletContext } from "react-router-dom";
import api from "../services/api";
import { useAuth } from "../context/AuthContext";

function ProjectsPage() {
    const { usuario } = useAuth();
    const { conversaCriada } = useOutletContext();
    const location = useLocation();
    const [projetos, setProjetos] = useState([]);
    const [conversas, setConversas] = useState([]);
    const [selecionado, setSelecionado] = useState(null);
    const [busca, setBusca] = useState("");
    const [modal, setModal] = useState(null);
    const [nome, setNome] = useState("");
    const [descricao, setDescricao] = useState("");
    const [salvando, setSalvando] = useState(false);

    async function carregar() {
        if (!usuario?.id_usuario) return;
        try {
            const [projetosResp, conversasResp] = await Promise.all([
                api.get(`/projetos/usuario/${usuario.id_usuario}`),
                api.get(`/conversas/usuario/${usuario.id_usuario}/todas`)
            ]);
            const listaProjetos = Array.isArray(projetosResp.data) ? projetosResp.data : [];
            setProjetos(listaProjetos);
            setConversas(Array.isArray(conversasResp.data) ? conversasResp.data : []);
            setSelecionado((atual) => atual ? listaProjetos.find((item) => item.id_projeto === atual.id_projeto) || null : listaProjetos[0] || null);
        } catch (erro) {
            console.error("Erro ao carregar projetos:", erro);
        }
    }

    useEffect(() => { carregar(); }, [usuario?.id_usuario]);

    useEffect(() => {
        const params = new URLSearchParams(location.search);
        if (params.get("novo") === "1") abrirNovoProjeto();
    }, [location.search]);

    function abrirNovoProjeto() {
        setNome("");
        setDescricao("");
        setModal("novo");
    }

    function abrirEditarProjeto(projeto) {
        setNome(projeto.nome);
        setDescricao(projeto.descricao || "");
        setModal("editar");
    }

    async function salvarProjeto(event) {
        event.preventDefault();
        if (!nome.trim() || salvando) return;
        setSalvando(true);
        try {
            if (modal === "novo") {
                const resposta = await api.post("/projetos", { id_usuario: usuario.id_usuario, nome: nome.trim(), descricao });
                setProjetos((lista) => [resposta.data, ...lista]);
                setSelecionado(resposta.data);
            } else {
                const resposta = await api.patch(`/projetos/${selecionado.id_projeto}`, { nome: nome.trim(), descricao });
                setProjetos((lista) => lista.map((item) => item.id_projeto === selecionado.id_projeto ? resposta.data : item));
                setSelecionado(resposta.data);
            }
            setModal(null);
            conversaCriada();
        } catch (erro) {
            console.error("Erro ao salvar projeto:", erro);
        } finally {
            setSalvando(false);
        }
    }

    async function excluirProjeto(projeto) {
        if (!window.confirm(`Excluir o projeto “${projeto.nome}”? As conversas não serão excluídas.`)) return;
        try {
            await api.delete(`/projetos/${projeto.id_projeto}`);
            setProjetos((lista) => lista.filter((item) => item.id_projeto !== projeto.id_projeto));
            setSelecionado((atual) => atual?.id_projeto === projeto.id_projeto ? null : atual);
            await carregar();
        } catch (erro) {
            console.error("Erro ao excluir projeto:", erro);
        }
    }

    async function removerConversa(conversa) {
        if (!selecionado) return;
        try {
            await api.delete(`/projetos/${selecionado.id_projeto}/conversas/${conversa.id_conversa}`);
            setConversas((lista) => lista.map((item) => item.id_conversa === conversa.id_conversa ? { ...item, id_projeto: null } : item));
            conversaCriada();
        } catch (erro) {
            console.error("Erro ao remover conversa do projeto:", erro);
        }
    }

    const conversasDoProjeto = useMemo(() => {
        if (!selecionado) return [];
        return conversas.filter((conversa) => conversa.id_projeto === selecionado.id_projeto);
    }, [conversas, selecionado]);

    const projetosFiltrados = projetos.filter((projeto) => projeto.nome.toLowerCase().includes(busca.toLowerCase()));

    return (
        <main className="ara-page projects-page">
            <header className="projects-hero">
                <div>
                    <span className="page-kicker">WORKSPACES</span>
                    <h1>Projetos</h1>
                    <p>Organize conversas por contexto e mantenha cada assunto no seu próprio espaço.</p>
                </div>
                <button className="projects-new-button" onClick={abrirNovoProjeto}><Plus size={18} /> Novo projeto</button>
            </header>

            <section className="projects-layout">
                <aside className="projects-list panel">
                    <div className="projects-list-heading">
                        <div><strong>Seus projetos</strong><span>{projetos.length} projetos</span></div>
                        <button onClick={abrirNovoProjeto} title="Novo projeto"><FolderPlus size={18} /></button>
                    </div>
                    <div className="projects-search"><Search size={16} /><input value={busca} onChange={(event) => setBusca(event.target.value)} placeholder="Pesquisar projeto" /></div>
                    <div className="project-items">
                        {projetosFiltrados.map((projeto) => (
                            <button key={projeto.id_projeto} className={selecionado?.id_projeto === projeto.id_projeto ? "project-item active" : "project-item"} onClick={() => setSelecionado(projeto)}>
                                <span className="project-item-icon"><FolderKanban size={17} /></span>
                                <span><strong>{projeto.nome}</strong><small>{conversas.filter((c) => c.id_projeto === projeto.id_projeto).length} conversas</small></span>
                            </button>
                        ))}
                        {projetos.length === 0 && <div className="project-empty"><FolderPlus size={27} /><strong>Crie seu primeiro projeto</strong><span>Depois, use os três pontos de qualquer conversa para colocá-la aqui.</span><button onClick={abrirNovoProjeto}>Criar projeto</button></div>}
                    </div>
                </aside>

                <section className="project-detail panel">
                    {selecionado ? (
                        <>
                            <header className="project-detail-header">
                                <div className="project-title-wrap">
                                    <span className="project-detail-icon"><FolderKanban size={24} /></span>
                                    <div><span className="page-kicker">PROJETO</span><h2>{selecionado.nome}</h2><p>{selecionado.descricao || "Sem descrição. Use este espaço para concentrar o contexto do projeto."}</p></div>
                                </div>
                                <div className="project-detail-actions">
                                    <button onClick={() => abrirEditarProjeto(selecionado)} title="Editar"><Edit3 size={17} /></button>
                                    <button className="danger" onClick={() => excluirProjeto(selecionado)} title="Excluir"><Trash2 size={17} /></button>
                                </div>
                            </header>

                            <div className="project-detail-stats">
                                <div><MessageSquare size={18} /><strong>{conversasDoProjeto.length}</strong><span>Conversas</span></div>
                                <div><Check size={18} /><strong>{conversasDoProjeto.filter((c) => c.status !== "ARQUIVADA").length}</strong><span>Ativas</span></div>
                                <div><Archive size={18} /><strong>{conversasDoProjeto.filter((c) => c.status === "ARQUIVADA").length}</strong><span>Arquivadas</span></div>
                            </div>

                            <div className="project-conversations-heading"><div><span className="page-kicker">CONTEÚDO</span><h3>Conversas deste projeto</h3></div><span>{conversasDoProjeto.length} itens</span></div>
                            <div className="project-conversations-list">
                                {conversasDoProjeto.map((conversa) => (
                                    <article className="project-conversation-row" key={conversa.id_conversa}>
                                        <span className="project-conversation-icon"><MessageSquare size={18} /></span>
                                        <div><strong>{conversa.titulo}</strong><small>{conversa.status === "ARQUIVADA" ? "Arquivada" : "Ativa"}</small></div>
                                        <button onClick={() => removerConversa(conversa)} title="Remover do projeto"><X size={16} /></button>
                                    </article>
                                ))}
                                {conversasDoProjeto.length === 0 && <div className="project-conversation-empty"><FolderKanban size={32} /><strong>Projeto vazio</strong><span>Abra os três pontos de uma conversa e escolha “Adicionar a projeto”.</span></div>}
                            </div>
                        </>
                    ) : (
                        <div className="project-detail-empty"><FolderKanban size={42} /><h2>Escolha um projeto</h2><p>Crie um projeto e comece a organizar suas conversas por assunto.</p><button onClick={abrirNovoProjeto}><FolderPlus size={17} /> Criar projeto</button></div>
                    )}
                </section>
            </section>

            {modal && (
                <div className="project-modal-backdrop" onMouseDown={(event) => event.target === event.currentTarget && setModal(null)}>
                    <form className="project-modal" onSubmit={salvarProjeto}>
                        <div className="project-modal-heading"><div><span className="page-kicker">{modal === "novo" ? "NOVO PROJETO" : "EDITAR PROJETO"}</span><h2>{modal === "novo" ? "Criar projeto" : "Editar projeto"}</h2></div><button type="button" onClick={() => setModal(null)}><X size={18} /></button></div>
                        <label>Nome<input autoFocus value={nome} onChange={(event) => setNome(event.target.value)} maxLength={120} placeholder="Ex.: Projeto A.R.A." /></label>
                        <label>Descrição<textarea value={descricao} onChange={(event) => setDescricao(event.target.value)} maxLength={5000} rows={4} placeholder="Descreva o objetivo deste projeto..." /></label>
                        <div className="project-modal-actions"><button type="button" onClick={() => setModal(null)}>Cancelar</button><button className="primary" disabled={salvando}>{salvando ? "Salvando..." : "Salvar projeto"}</button></div>
                    </form>
                </div>
            )}
        </main>
    );
}

export default ProjectsPage;
