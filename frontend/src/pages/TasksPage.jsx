import { useCallback, useEffect, useMemo, useState } from "react";
import {
    Check,
    CirclePlay,
    Clock3,
    Edit3,
    MoreHorizontal,
    Plus,
    RotateCcw,
    Trash2,
    X
} from "lucide-react";
import api from "../services/api";
import { useAuth } from "../context/AuthContext";

const FILTROS = [
    ["TODAS", "Todas"],
    ["PENDENTE", "Pendentes"],
    ["EM_ANDAMENTO", "Em andamento"],
    ["CONCLUIDA", "Concluídas"],
    ["CANCELADA", "Canceladas"]
];

const ESTADO_INICIAL = {
    titulo: "",
    descricao: "",
    prioridade: 3,
    dataLimite: ""
};

function limitarAnoDateTime(valor) {
    if (!valor) return "";

    // datetime-local pode permitir que o usuário digite mais de 4 dígitos no ano.
    // Mantemos o formato ISO e limitamos o ano a exatamente 4 dígitos.
    const correspondencia = valor.match(/^(\d+)(-.+)$/);
    if (correspondencia && correspondencia[1].length > 4) {
        return `${correspondencia[1].slice(0, 4)}${correspondencia[2]}`;
    }

    return valor;
}

function paraInputDateTime(data) {
    if (!data) return "";
    const valor = new Date(data);
    if (Number.isNaN(valor.getTime())) return "";

    const pad = (numero) => String(numero).padStart(2, "0");
    return `${valor.getFullYear()}-${pad(valor.getMonth() + 1)}-${pad(valor.getDate())}T${pad(valor.getHours())}:${pad(valor.getMinutes())}`;
}

function formatarData(data) {
    if (!data) return "Sem prazo";
    const valor = new Date(data);
    if (Number.isNaN(valor.getTime())) return "Data inválida";

    return valor.toLocaleString("pt-BR", {
        day: "2-digit",
        month: "2-digit",
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit"
    });
}

function formatarStatus(status) {
    const mapa = {
        PENDENTE: "Pendente",
        EM_ANDAMENTO: "Em andamento",
        CONCLUIDA: "Concluída",
        CANCELADA: "Cancelada"
    };
    return mapa[status] || status;
}

function TasksPage() {
    const { usuario } = useAuth();
    const [tarefas, setTarefas] = useState([]);
    const [filtro, setFiltro] = useState("TODAS");
    const [carregando, setCarregando] = useState(true);
    const [salvando, setSalvando] = useState(false);
    const [modal, setModal] = useState(null); // "criar" | "editar"
    const [tarefaEditando, setTarefaEditando] = useState(null);
    const [menuAberto, setMenuAberto] = useState(null);
    const [form, setForm] = useState(ESTADO_INICIAL);

    const carregarTarefas = useCallback(async (mostrarCarregamento = true) => {
        if (!usuario?.id_usuario) return;
        if (mostrarCarregamento) setCarregando(true);

        try {
            const resposta = await api.get(`/tarefas/usuario/${usuario.id_usuario}`, {
                params: { _: Date.now() }
            });
            setTarefas(Array.isArray(resposta.data) ? resposta.data : []);
        } catch (erro) {
            console.error("Erro ao carregar tarefas:", erro);
        } finally {
            if (mostrarCarregamento) setCarregando(false);
        }
    }, [usuario?.id_usuario]);

    useEffect(() => {
        carregarTarefas();

        const atualizar = () => carregarTarefas(false);
        const foco = () => carregarTarefas(false);
        const visibilidade = () => {
            if (document.visibilityState === "visible") carregarTarefas(false);
        };

        window.addEventListener("jarvis:tarefas-atualizadas", atualizar);
        window.addEventListener("focus", foco);
        document.addEventListener("visibilitychange", visibilidade);

        return () => {
            window.removeEventListener("jarvis:tarefas-atualizadas", atualizar);
            window.removeEventListener("focus", foco);
            document.removeEventListener("visibilitychange", visibilidade);
        };
    }, [carregarTarefas]);

    function atualizarCampo(campo, valor) {
        setForm((anterior) => ({ ...anterior, [campo]: valor }));
    }

    function abrirCriacao() {
        setTarefaEditando(null);
        setForm(ESTADO_INICIAL);
        setModal("criar");
    }

    function abrirEdicao(tarefa) {
        setTarefaEditando(tarefa);
        setForm({
            titulo: tarefa.titulo || "",
            descricao: tarefa.descricao || "",
            prioridade: tarefa.prioridade || 3,
            dataLimite: paraInputDateTime(tarefa.data_limite)
        });
        setMenuAberto(null);
        setModal("editar");
    }

    function fecharModal() {
        if (salvando) return;
        setModal(null);
        setTarefaEditando(null);
        setForm(ESTADO_INICIAL);
    }

    async function salvarTarefa(event) {
        event.preventDefault();
        const titulo = form.titulo.trim();
        if (!titulo || salvando || !usuario?.id_usuario) return;

        setSalvando(true);

        try {
            const payload = {
                titulo,
                descricao: form.descricao.trim(),
                prioridade: Number(form.prioridade),
                data_limite: form.dataLimite
                    ? new Date(form.dataLimite).toISOString()
                    : null
            };

            if (modal === "criar") {
                await api.post("/tarefas", {
                    id_usuario: usuario.id_usuario,
                    ...payload
                });
            } else {
                await api.patch(`/tarefas/${tarefaEditando.id_tarefa}`, {
                    ...payload,
                    remover_data_limite: !form.dataLimite
                });
            }

            await carregarTarefas(false);
            fecharModal();
        } catch (erro) {
            console.error("Erro ao salvar tarefa:", erro);
            alert(erro.response?.data?.detail || "Não foi possível salvar a tarefa.");
        } finally {
            setSalvando(false);
        }
    }

    function atualizarTarefaLocal(tarefaAtualizada) {
        if (!tarefaAtualizada?.id_tarefa) return;
        setTarefas((anteriores) => anteriores.map((tarefa) => (
            tarefa.id_tarefa === tarefaAtualizada.id_tarefa ? tarefaAtualizada : tarefa
        )));
    }

    async function executarAcao(idTarefa, endpoint, mensagem) {
        try {
            const resposta = await api.patch(`/tarefas/${idTarefa}/${endpoint}`);
            atualizarTarefaLocal(resposta.data);
            setMenuAberto(null);
        } catch (erro) {
            console.error(mensagem, erro);
            alert(erro.response?.data?.detail || mensagem);
        }
    }

    async function iniciarTarefa(idTarefa) {
        await executarAcao(idTarefa, "iniciar", "Não foi possível iniciar a tarefa.");
    }

    async function concluirTarefa(idTarefa) {
        await executarAcao(idTarefa, "concluir", "Não foi possível concluir a tarefa.");
    }

    async function cancelarTarefa(idTarefa) {
        if (!window.confirm("Cancelar esta tarefa?")) return;
        await executarAcao(idTarefa, "cancelar", "Não foi possível cancelar a tarefa.");
    }

    async function reabrirTarefa(idTarefa) {
        await executarAcao(idTarefa, "reabrir", "Não foi possível reabrir a tarefa.");
    }

    async function excluirTarefa(idTarefa) {
        if (!window.confirm("Excluir esta tarefa definitivamente?")) return;

        try {
            await api.delete(`/tarefas/${idTarefa}`);
            setTarefas((anteriores) => anteriores.filter((tarefa) => tarefa.id_tarefa !== idTarefa));
            setMenuAberto(null);
        } catch (erro) {
            console.error("Erro ao excluir tarefa:", erro);
            alert(erro.response?.data?.detail || "Não foi possível excluir a tarefa.");
        }
    }

    const tarefasFiltradas = useMemo(() => {
        if (filtro === "TODAS") return tarefas;
        return tarefas.filter((tarefa) => tarefa.status === filtro);
    }, [tarefas, filtro]);

    const resumo = useMemo(() => ({
        abertas: tarefas.filter((t) => ["PENDENTE", "EM_ANDAMENTO"].includes(t.status)).length,
        andamento: tarefas.filter((t) => t.status === "EM_ANDAMENTO").length,
        concluidas: tarefas.filter((t) => t.status === "CONCLUIDA").length,
        canceladas: tarefas.filter((t) => t.status === "CANCELADA").length
    }), [tarefas]);

    return (
        <main className="tasks-page">
            <header className="tasks-header">
                <div className="tasks-heading-copy">
                    <span className="page-kicker">ORGANIZAÇÃO</span>
                    <h1>Tarefas</h1>
                    <p>Organize suas atividades, defina prioridades e acompanhe seu progresso.</p>
                </div>

                <button className="task-create-button" onClick={abrirCriacao}>
                    <Plus size={18} />
                    Nova tarefa
                </button>
            </header>

            <section className="tasks-content">
                <div className="task-summary-grid">
                    <article><span>Em aberto</span><strong>{carregando ? "—" : resumo.abertas}</strong></article>
                    <article><span>Em andamento</span><strong>{carregando ? "—" : resumo.andamento}</strong></article>
                    <article><span>Concluídas</span><strong>{carregando ? "—" : resumo.concluidas}</strong></article>
                    <article><span>Canceladas</span><strong>{carregando ? "—" : resumo.canceladas}</strong></article>
                </div>

                <div className="tasks-section-heading">
                    <div>
                        <span className="feature-label">SEU FLUXO</span>
                        <h2>Lista de tarefas</h2>
                    </div>
                    <span className="tasks-count">{tarefasFiltradas.length} {tarefasFiltradas.length === 1 ? "tarefa" : "tarefas"}</span>
                </div>

                <div className="task-filters">
                    {FILTROS.map(([valor, texto]) => (
                        <button
                            key={valor}
                            className={filtro === valor ? "task-filter active" : "task-filter"}
                            onClick={() => setFiltro(valor)}
                        >
                            {texto}
                        </button>
                    ))}
                </div>

                {carregando && <div className="task-empty"><Clock3 size={24} /><strong>Carregando suas tarefas...</strong><span>Buscando os dados mais recentes.</span></div>}

                {!carregando && tarefasFiltradas.length === 0 && (
                    <div className="task-empty">
                        <Check size={26} />
                        <strong>{filtro === "TODAS" ? "Nenhuma tarefa ainda" : "Nenhuma tarefa neste filtro"}</strong>
                        <span>{filtro === "TODAS" ? "Crie sua primeira tarefa para começar a organizar seu dia." : "Altere o filtro ou crie uma nova tarefa."}</span>
                        {filtro === "TODAS" && <button className="empty-create-button" onClick={abrirCriacao}><Plus size={16} /> Criar primeira tarefa</button>}
                    </div>
                )}

                {!carregando && tarefasFiltradas.length > 0 && (
                    <div className="task-list">
                        {tarefasFiltradas.map((tarefa) => (
                            <article key={tarefa.id_tarefa} className={`task-card task-status-${tarefa.status.toLowerCase()}`}>
                                <div className="task-card-top">
                                    <div className="task-main-copy">
                                        <div className="task-title-row">
                                            <h3>{tarefa.titulo}</h3>
                                            <span className={`task-priority priority-${tarefa.prioridade}`}>Prioridade {tarefa.prioridade}</span>
                                        </div>
                                        {tarefa.descricao && <p className="task-description">{tarefa.descricao}</p>}
                                    </div>

                                    <div className="task-menu-container">
                                        <button
                                            className="task-menu-button"
                                            onClick={() => setMenuAberto(menuAberto === tarefa.id_tarefa ? null : tarefa.id_tarefa)}
                                            aria-label="Mais opções"
                                        >
                                            <MoreHorizontal size={20} />
                                        </button>

                                        {menuAberto === tarefa.id_tarefa && (
                                            <div className="task-menu">
                                                <button onClick={() => abrirEdicao(tarefa)}><Edit3 size={15} /> Editar</button>

                                                {tarefa.status !== "CONCLUIDA" && tarefa.status !== "CANCELADA" && (
                                                    <button onClick={() => cancelarTarefa(tarefa.id_tarefa)}><X size={15} /> Cancelar</button>
                                                )}

                                                {(tarefa.status === "CONCLUIDA" || tarefa.status === "CANCELADA") && (
                                                    <button onClick={() => reabrirTarefa(tarefa.id_tarefa)}><RotateCcw size={15} /> Reabrir</button>
                                                )}

                                                <button className="danger" onClick={() => excluirTarefa(tarefa.id_tarefa)}><Trash2 size={15} /> Excluir</button>
                                            </div>
                                        )}
                                    </div>
                                </div>

                                <div className="task-meta">
                                    <span>Status <strong>{formatarStatus(tarefa.status)}</strong></span>
                                    <span>Prazo <strong>{formatarData(tarefa.data_limite)}</strong></span>
                                </div>

                                <div className="task-actions">
                                    {tarefa.status === "PENDENTE" && (
                                        <button onClick={() => iniciarTarefa(tarefa.id_tarefa)}><CirclePlay size={16} /> Iniciar</button>
                                    )}

                                    {(tarefa.status === "PENDENTE" || tarefa.status === "EM_ANDAMENTO") && (
                                        <button className="primary" onClick={() => concluirTarefa(tarefa.id_tarefa)}><Check size={16} /> Concluir</button>
                                    )}

                                    {tarefa.status === "CONCLUIDA" && <span className="task-finished"><Check size={16} /> Concluída</span>}
                                    {tarefa.status === "CANCELADA" && <span className="task-cancelled"><X size={16} /> Cancelada</span>}
                                </div>
                            </article>
                        ))}
                    </div>
                )}
            </section>

            {modal && (
                <div className="task-modal-overlay" onMouseDown={fecharModal}>
                    <form className="task-modal" onSubmit={salvarTarefa} onMouseDown={(event) => event.stopPropagation()}>
                        <div className="task-modal-header">
                            <div>
                                <span className="page-kicker">{modal === "criar" ? "NOVA ATIVIDADE" : "ALTERAR ATIVIDADE"}</span>
                                <h2>{modal === "criar" ? "Nova tarefa" : "Editar tarefa"}</h2>
                                <p>{modal === "criar" ? "Adicione uma atividade ao seu fluxo." : "Atualize as informações desta tarefa."}</p>
                            </div>
                            <button type="button" onClick={fecharModal} disabled={salvando} aria-label="Fechar"><X size={20} /></button>
                        </div>

                        <label>Título
                            <input type="text" value={form.titulo} onChange={(event) => atualizarCampo("titulo", event.target.value)} maxLength={200} autoFocus required />
                        </label>

                        <label>Descrição
                            <textarea value={form.descricao} onChange={(event) => atualizarCampo("descricao", event.target.value)} rows={4} placeholder="Descreva o que precisa ser feito..." />
                        </label>

                        <div className="task-form-row">
                            <label>Prioridade
                                <select value={form.prioridade} onChange={(event) => atualizarCampo("prioridade", Number(event.target.value))}>
                                    <option value={1}>1 — Muito baixa</option>
                                    <option value={2}>2 — Baixa</option>
                                    <option value={3}>3 — Normal</option>
                                    <option value={4}>4 — Alta</option>
                                    <option value={5}>5 — Urgente</option>
                                </select>
                            </label>

                            <label>Prazo
                                <input type="datetime-local" value={form.dataLimite} onChange={(event) => atualizarCampo("dataLimite", limitarAnoDateTime(event.target.value))} max="9999-12-31T23:59" />
                            </label>
                        </div>

                        <div className="task-modal-actions">
                            <button type="button" onClick={fecharModal} disabled={salvando}>Cancelar</button>
                            <button type="submit" className="primary" disabled={salvando || !form.titulo.trim()}>
                                {modal === "criar" ? <Plus size={17} /> : <Check size={17} />}
                                {salvando ? "Salvando..." : modal === "criar" ? "Criar tarefa" : "Salvar alterações"}
                            </button>
                        </div>
                    </form>
                </div>
            )}
        </main>
    );
}

export default TasksPage;