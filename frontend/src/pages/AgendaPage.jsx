import { useCallback, useEffect, useMemo, useState } from "react";
import {
    BellRing,
    CalendarDays,
    Check,
    ChevronLeft,
    ChevronRight,
    Clock3,
    Edit3,
    MoreHorizontal,
    Plus,
    Trash2,
    X
} from "lucide-react";
import api from "../services/api";
import { useAuth } from "../context/AuthContext";

const FORM_INICIAL = {
    titulo: "",
    descricao: "",
    dataHora: "",
    recorrencia: ""
};

const NOMES_DIAS = ["Dom", "Seg", "Ter", "Qua", "Qui", "Sex", "Sáb"];

function inicioDoDia(data) {
    const valor = new Date(data);
    valor.setHours(0, 0, 0, 0);
    return valor;
}

function chaveDia(data) {
    const valor = new Date(data);
    const pad = (numero) => String(numero).padStart(2, "0");
    return `${valor.getFullYear()}-${pad(valor.getMonth() + 1)}-${pad(valor.getDate())}`;
}

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

function paraPayloadDateTime(valor) {
    if (!valor) return null;
    return `${valor}:00`;
}

function formatarHora(data) {
    return new Date(data).toLocaleTimeString("pt-BR", {
        hour: "2-digit",
        minute: "2-digit"
    });
}

function formatarDataCompleta(data) {
    return new Date(data).toLocaleDateString("pt-BR", {
        weekday: "long",
        day: "2-digit",
        month: "long"
    });
}

function formatarRecorrencia(valor) {
    const mapa = {
        DIARIA: "Todos os dias",
        SEMANAL: "Toda semana",
        MENSAL: "Todo mês"
    };
    return mapa[valor] || "Sem repetição";
}

function mesmoDia(a, b) {
    return chaveDia(a) === chaveDia(b);
}

function AgendaPage() {
    const { usuario } = useAuth();
    const hoje = useMemo(() => inicioDoDia(new Date()), []);
    const [diaSelecionado, setDiaSelecionado] = useState(hoje);
    const [eventos, setEventos] = useState([]);
    const [carregando, setCarregando] = useState(true);
    const [salvando, setSalvando] = useState(false);
    const [modal, setModal] = useState(null);
    const [eventoEditando, setEventoEditando] = useState(null);
    const [menuAberto, setMenuAberto] = useState(null);
    const [form, setForm] = useState(FORM_INICIAL);

    const carregarAgenda = useCallback(async (mostrarCarregamento = true) => {
        if (!usuario?.id_usuario) return;
        if (mostrarCarregamento) setCarregando(true);

        try {
            const resposta = await api.get(`/agenda/usuario/${usuario.id_usuario}`, {
                params: { _: Date.now() }
            });
            setEventos(Array.isArray(resposta.data) ? resposta.data : []);
        } catch (erro) {
            console.error("Erro ao carregar agenda:", erro);
            alert(erro.response?.data?.detail || "Não foi possível carregar sua agenda.");
        } finally {
            if (mostrarCarregamento) setCarregando(false);
        }
    }, [usuario?.id_usuario]);

    useEffect(() => {
        carregarAgenda();

        const atualizar = () => carregarAgenda(false);
        const visibilidade = () => {
            if (document.visibilityState === "visible") carregarAgenda(false);
        };

        window.addEventListener("ara:agenda-atualizada", atualizar);
        window.addEventListener("focus", atualizar);
        document.addEventListener("visibilitychange", visibilidade);

        return () => {
            window.removeEventListener("ara:agenda-atualizada", atualizar);
            window.removeEventListener("focus", atualizar);
            document.removeEventListener("visibilitychange", visibilidade);
        };
    }, [carregarAgenda]);

    const diasDaSemana = useMemo(() => {
        const inicio = new Date(diaSelecionado);
        const domingo = new Date(inicio);
        domingo.setDate(inicio.getDate() - inicio.getDay());
        domingo.setHours(0, 0, 0, 0);

        return Array.from({ length: 7 }, (_, indice) => {
            const dia = new Date(domingo);
            dia.setDate(domingo.getDate() + indice);
            return dia;
        });
    }, [diaSelecionado]);

    const eventosDoDia = useMemo(() => {
        return eventos
            .filter((evento) => mesmoDia(evento.data_hora, diaSelecionado))
            .sort((a, b) => new Date(a.data_hora) - new Date(b.data_hora));
    }, [eventos, diaSelecionado]);

    const resumo = useMemo(() => {
        const ativos = eventos.filter((evento) => ["PENDENTE", "EM_ANDAMENTO"].includes(evento.status));
        return {
            hoje: eventos.filter((evento) => mesmoDia(evento.data_hora, hoje) && evento.status !== "CANCELADA").length,
            proximos: ativos.filter((evento) => new Date(evento.data_hora) >= new Date()).length,
            pendentes: ativos.length,
            concluidos: eventos.filter((evento) => evento.status === "CONCLUIDA").length
        };
    }, [eventos, hoje]);

    function mudarDia(dias) {
        setDiaSelecionado((anterior) => {
            const novo = new Date(anterior);
            novo.setDate(novo.getDate() + dias);
            return novo;
        });
    }

    function irParaHoje() {
        setDiaSelecionado(inicioDoDia(new Date()));
    }

    function abrirCriacao() {
        setEventoEditando(null);
        setForm({
            ...FORM_INICIAL,
            dataHora: paraInputDateTime(new Date(diaSelecionado).setHours(9, 0, 0, 0))
        });
        setModal("criar");
        setMenuAberto(null);
    }

    function abrirEdicao(evento) {
        setEventoEditando(evento);
        setForm({
            titulo: evento.titulo || "",
            descricao: evento.descricao || "",
            dataHora: paraInputDateTime(evento.data_hora),
            recorrencia: evento.recorrencia || ""
        });
        setModal("editar");
        setMenuAberto(null);
    }

    function fecharModal() {
        if (salvando) return;
        setModal(null);
        setEventoEditando(null);
        setForm(FORM_INICIAL);
    }

    function atualizarCampo(campo, valor) {
        setForm((anterior) => ({ ...anterior, [campo]: valor }));
    }

    async function salvarEvento(event) {
        event.preventDefault();
        if (salvando || !usuario?.id_usuario || !form.titulo.trim() || !form.dataHora) return;

        setSalvando(true);

        try {
            const payload = {
                titulo: form.titulo.trim(),
                descricao: form.descricao.trim() || null,
                data_hora: paraPayloadDateTime(form.dataHora),
                recorrencia: form.recorrencia || null
            };

            if (modal === "criar") {
                await api.post("/agenda", {
                    id_usuario: usuario.id_usuario,
                    ...payload
                });
            } else {
                await api.patch(`/agenda/${eventoEditando.id_lembrete}`, payload, {
                    params: { id_usuario: usuario.id_usuario }
                });
            }

            await carregarAgenda(false);
            window.dispatchEvent(new Event("ara:agenda-atualizada"));
            fecharModal();
        } catch (erro) {
            console.error("Erro ao salvar evento:", erro);
            alert(erro.response?.data?.detail || "Não foi possível salvar o evento.");
        } finally {
            setSalvando(false);
        }
    }

    async function alterarStatus(evento, status) {
        try {
            const resposta = await api.patch(`/agenda/${evento.id_lembrete}`, { status }, {
                params: { id_usuario: usuario.id_usuario }
            });
            setEventos((anteriores) => anteriores.map((item) => (
                item.id_lembrete === evento.id_lembrete ? resposta.data : item
            )));
            setMenuAberto(null);
        } catch (erro) {
            console.error("Erro ao atualizar evento:", erro);
            alert(erro.response?.data?.detail || "Não foi possível atualizar o evento.");
        }
    }

    async function excluirEvento(evento) {
        if (!window.confirm(`Excluir "${evento.titulo}" da agenda?`)) return;

        try {
            await api.delete(`/agenda/${evento.id_lembrete}`, {
                params: { id_usuario: usuario.id_usuario }
            });
            setEventos((anteriores) => anteriores.filter((item) => item.id_lembrete !== evento.id_lembrete));
            setMenuAberto(null);
        } catch (erro) {
            console.error("Erro ao excluir evento:", erro);
            alert(erro.response?.data?.detail || "Não foi possível excluir o evento.");
        }
    }

    return (
        <main className="ara-page agenda-page">
            <header className="agenda-header">
                <div className="agenda-heading-copy">
                    <span className="page-kicker">TEMPO & ROTINA</span>
                    <h1>Agenda</h1>
                    <p>Organize compromissos, lembretes e horários importantes em um só lugar.</p>
                </div>

                <button className="agenda-create-button" onClick={abrirCriacao}>
                    <Plus size={18} />
                    Novo evento
                </button>
            </header>

            <section className="agenda-summary-grid">
                <article><span><CalendarDays size={17} /> Hoje</span><strong>{carregando ? "—" : resumo.hoje}</strong><small>eventos marcados</small></article>
                <article><span><Clock3 size={17} /> Próximos</span><strong>{carregando ? "—" : resumo.proximos}</strong><small>a partir de agora</small></article>
                <article><span><BellRing size={17} /> Pendentes</span><strong>{carregando ? "—" : resumo.pendentes}</strong><small>aguardando ação</small></article>
                <article><span><Check size={17} /> Concluídos</span><strong>{carregando ? "—" : resumo.concluidos}</strong><small>eventos finalizados</small></article>
            </section>

            <section className="agenda-calendar panel">
                <div className="agenda-calendar-top">
                    <div>
                        <span className="feature-label">CALENDÁRIO</span>
                        <h2>{formatarDataCompleta(diaSelecionado)}</h2>
                    </div>
                    <div className="agenda-calendar-actions">
                        <button onClick={irParaHoje}>Hoje</button>
                        <button onClick={() => mudarDia(-7)} aria-label="Semana anterior"><ChevronLeft size={18} /></button>
                        <button onClick={() => mudarDia(7)} aria-label="Próxima semana"><ChevronRight size={18} /></button>
                    </div>
                </div>

                <div className="agenda-week">
                    {diasDaSemana.map((dia) => {
                        const selecionado = mesmoDia(dia, diaSelecionado);
                        const hojeDia = mesmoDia(dia, hoje);
                        const quantidade = eventos.filter((evento) => mesmoDia(evento.data_hora, dia) && evento.status !== "CANCELADA").length;

                        return (
                            <button
                                key={chaveDia(dia)}
                                className={`agenda-day ${selecionado ? "selected" : ""} ${hojeDia ? "today" : ""}`}
                                onClick={() => setDiaSelecionado(dia)}
                            >
                                <span>{NOMES_DIAS[dia.getDay()]}</span>
                                <strong>{dia.getDate()}</strong>
                                {quantidade > 0 && <small>{quantidade}</small>}
                            </button>
                        );
                    })}
                </div>
            </section>

            <section className="agenda-events-section">
                <div className="agenda-section-heading">
                    <div>
                        <span className="feature-label">PROGRAMAÇÃO</span>
                        <h2>Eventos do dia</h2>
                    </div>
                    <span>{eventosDoDia.length} {eventosDoDia.length === 1 ? "evento" : "eventos"}</span>
                </div>

                {carregando && (
                    <div className="agenda-empty">
                        <Clock3 size={25} />
                        <strong>Carregando sua agenda...</strong>
                        <span>Buscando os eventos mais recentes.</span>
                    </div>
                )}

                {!carregando && eventosDoDia.length === 0 && (
                    <div className="agenda-empty">
                        <CalendarDays size={28} />
                        <strong>Nenhum evento neste dia</strong>
                        <span>Use a agenda para marcar compromissos, lembretes ou horários importantes.</span>
                        <button onClick={abrirCriacao}><Plus size={16} /> Criar evento</button>
                    </div>
                )}

                {!carregando && eventosDoDia.length > 0 && (
                    <div className="agenda-event-list">
                        {eventosDoDia.map((evento) => (
                            <article key={evento.id_lembrete} className={`agenda-event-card agenda-event-${evento.status.toLowerCase()}`}>
                                <div className="agenda-event-time">
                                    <strong>{formatarHora(evento.data_hora)}</strong>
                                    <span>{evento.status === "CONCLUIDA" ? "Concluído" : evento.status === "CANCELADA" ? "Cancelado" : "Programado"}</span>
                                </div>

                                <div className="agenda-event-main">
                                    <div className="agenda-event-title-row">
                                        <h3>{evento.titulo}</h3>
                                        <div className="agenda-menu-container">
                                            <button className="agenda-menu-button" onClick={() => setMenuAberto(menuAberto === evento.id_lembrete ? null : evento.id_lembrete)} aria-label="Mais opções">
                                                <MoreHorizontal size={19} />
                                            </button>
                                            {menuAberto === evento.id_lembrete && (
                                                <div className="agenda-menu">
                                                    <button onClick={() => abrirEdicao(evento)}><Edit3 size={15} /> Editar</button>
                                                    {evento.status !== "CONCLUIDA" && evento.status !== "CANCELADA" && (
                                                        <button onClick={() => alterarStatus(evento, "CONCLUIDA")}><Check size={15} /> Concluir</button>
                                                    )}
                                                    {evento.status === "CANCELADA" && (
                                                        <button onClick={() => alterarStatus(evento, "PENDENTE")}><BellRing size={15} /> Reabrir</button>
                                                    )}
                                                    {evento.status === "CONCLUIDA" && (
                                                        <button onClick={() => alterarStatus(evento, "PENDENTE")}><BellRing size={15} /> Reabrir</button>
                                                    )}
                                                    <button className="danger" onClick={() => excluirEvento(evento)}><Trash2 size={15} /> Excluir</button>
                                                </div>
                                            )}
                                        </div>
                                    </div>

                                    {evento.descricao && <p>{evento.descricao}</p>}
                                    <div className="agenda-event-meta">
                                        <span>{formatarRecorrencia(evento.recorrencia)}</span>
                                        <span>{evento.status === "PENDENTE" ? "Pendente" : evento.status === "EM_ANDAMENTO" ? "Em andamento" : evento.status === "CONCLUIDA" ? "Concluído" : "Cancelado"}</span>
                                    </div>
                                </div>
                            </article>
                        ))}
                    </div>
                )}
            </section>

            {modal && (
                <div className="agenda-modal-overlay" onMouseDown={fecharModal}>
                    <form className="agenda-modal" onSubmit={salvarEvento} onMouseDown={(event) => event.stopPropagation()}>
                        <div className="agenda-modal-header">
                            <div>
                                <span className="page-kicker">{modal === "criar" ? "NOVO EVENTO" : "ALTERAR EVENTO"}</span>
                                <h2>{modal === "criar" ? "Adicionar à agenda" : "Editar evento"}</h2>
                                <p>{modal === "criar" ? "Defina quando a A.R.A. deve lembrar você." : "Atualize os detalhes deste evento."}</p>
                            </div>
                            <button type="button" onClick={fecharModal} disabled={salvando} aria-label="Fechar"><X size={20} /></button>
                        </div>

                        <label>Título
                            <input value={form.titulo} onChange={(event) => atualizarCampo("titulo", event.target.value)} maxLength={200} autoFocus required placeholder="Ex.: Reunião com cliente" />
                        </label>

                        <label>Descrição
                            <textarea value={form.descricao} onChange={(event) => atualizarCampo("descricao", event.target.value)} rows={4} maxLength={5000} placeholder="Adicione detalhes, local, pessoas ou observações..." />
                        </label>

                        <div className="agenda-form-row">
                            <label>Data e hora
                                <input type="datetime-local" value={form.dataHora} onChange={(event) => atualizarCampo("dataHora", limitarAnoDateTime(event.target.value))} max="9999-12-31T23:59" required />
                            </label>
                            <label>Repetição
                                <select value={form.recorrencia} onChange={(event) => atualizarCampo("recorrencia", event.target.value)}>
                                    <option value="">Não repetir</option>
                                    <option value="DIARIA">Todos os dias</option>
                                    <option value="SEMANAL">Toda semana</option>
                                    <option value="MENSAL">Todo mês</option>
                                </select>
                            </label>
                        </div>

                        <div className="agenda-modal-actions">
                            <button type="button" onClick={fecharModal} disabled={salvando}>Cancelar</button>
                            <button type="submit" className="primary" disabled={salvando || !form.titulo.trim() || !form.dataHora}>
                                {modal === "criar" ? <Plus size={17} /> : <Check size={17} />}
                                {salvando ? "Salvando..." : modal === "criar" ? "Criar evento" : "Salvar alterações"}
                            </button>
                        </div>
                    </form>
                </div>
            )}
        </main>
    );
}

export default AgendaPage;
