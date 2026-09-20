import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
    ArrowRight,
    CalendarDays,
    CheckCircle2,
    Clock3,
    ListTodo,
    MessageSquareText,
    Sparkles,
    Zap
} from "lucide-react";
import api from "../services/api";
import { useAuth } from "../context/AuthContext";

function saudacao() {
    const hora = new Date().getHours();
    if (hora < 12) return "Bom dia";
    if (hora < 18) return "Boa tarde";
    return "Boa noite";
}

function HomePage() {
    const { usuario } = useAuth();
    const navigate = useNavigate();
    const [tarefas, setTarefas] = useState([]);
    const [carregando, setCarregando] = useState(true);

    useEffect(() => {
        let ativo = true;
        async function carregar() {
            if (!usuario?.id_usuario) return;
            try {
                const resposta = await api.get(`/tarefas/usuario/${usuario.id_usuario}`);
                if (ativo) setTarefas(Array.isArray(resposta.data) ? resposta.data : []);
            } catch (erro) {
                console.error("Erro ao montar visão Hoje:", erro);
            } finally {
                if (ativo) setCarregando(false);
            }
        }
        carregar();
        return () => { ativo = false; };
    }, [usuario?.id_usuario]);

    const resumo = useMemo(() => {
        const pendentes = tarefas.filter((t) => !["CONCLUIDA", "CANCELADA"].includes(t.status));
        const concluidas = tarefas.filter((t) => t.status === "CONCLUIDA");
        const comPrazo = pendentes.filter((t) => t.data_limite);
        const proxima = [...comPrazo].sort((a, b) => new Date(a.data_limite) - new Date(b.data_limite))[0];
        return { pendentes, concluidas, proxima };
    }, [tarefas]);

    const primeiroNome = usuario?.nome?.split(" ")?.[0] || "";
    const data = new Intl.DateTimeFormat("pt-BR", {
        weekday: "long", day: "2-digit", month: "long"
    }).format(new Date());

    return (
        <main className="ara-page home-page">
            <section className="home-hero">
                <div>
                    <span className="page-kicker"><Sparkles size={15} /> VISÃO DE HOJE</span>
                    <h1>{saudacao()}{primeiroNome ? `, ${primeiroNome}.` : "."}</h1>
                    <p className="home-date">{data}</p>
                    <p className="home-lead">A.R.A. organiza o que importa e mantém seus próximos movimentos visíveis.</p>
                </div>
                <button className="hero-action" onClick={() => navigate("/chat")}>
                    Conversar com A.R.A. <ArrowRight size={18} />
                </button>
            </section>

            <section className="metric-grid">
                <article className="metric-card"><span><ListTodo size={18} /></span><strong>{carregando ? "—" : resumo.pendentes.length}</strong><p>Tarefas em aberto</p></article>
                <article className="metric-card"><span><CheckCircle2 size={18} /></span><strong>{carregando ? "—" : resumo.concluidas.length}</strong><p>Concluídas</p></article>
                <article className="metric-card"><span><CalendarDays size={18} /></span><strong>{resumo.proxima ? "1" : "0"}</strong><p>Próximo prazo</p></article>
                <article className="metric-card signal"><span><Zap size={18} /></span><strong>ONLINE</strong><p>Núcleo operacional</p></article>
            </section>

            <section className="home-grid">
                <article className="panel next-panel">
                    <div className="panel-heading"><div><span className="page-kicker">PRÓXIMO FOCO</span><h2>O que vem agora</h2></div><Clock3 size={20} /></div>
                    {resumo.proxima ? (
                        <div className="next-task">
                            <strong>{resumo.proxima.titulo}</strong>
                            <span>{new Intl.DateTimeFormat("pt-BR", { dateStyle: "medium", timeStyle: "short" }).format(new Date(resumo.proxima.data_limite))}</span>
                            <button onClick={() => navigate("/tarefas")}>Abrir tarefas <ArrowRight size={16} /></button>
                        </div>
                    ) : (
                        <div className="panel-empty">Nenhum prazo futuro identificado. Você pode planejar uma nova tarefa quando quiser.</div>
                    )}
                </article>

                <article className="panel quick-panel">
                    <div className="panel-heading"><div><span className="page-kicker">ATALHOS</span><h2>Ações rápidas</h2></div></div>
                    <div className="quick-actions">
                        <button onClick={() => navigate("/chat")}><MessageSquareText size={18} /><span><strong>Nova conversa</strong><small>Pensar, pesquisar ou executar</small></span></button>
                        <button onClick={() => navigate("/tarefas")}><ListTodo size={18} /><span><strong>Tarefas</strong><small>Organize prioridades e prazos</small></span></button>
                        <button onClick={() => navigate("/agenda")}><CalendarDays size={18} /><span><strong>Agenda</strong><small>Planeje compromissos</small></span></button>
                    </div>
                </article>
            </section>
        </main>
    );
}

export default HomePage;
