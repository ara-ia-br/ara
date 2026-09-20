import { useEffect, useMemo, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
    Archive,
    Bot,
    CalendarDays,
    FileText,
    FolderKanban,
    ListTodo,
    MemoryStick,
    Search,
    Settings2,
    Sparkles,
    Workflow,
    X
} from "lucide-react";

const commands = [
    { label: "Abrir A.R.A.", detail: "Ir para o workspace de conversa", path: "/chat", icon: Bot },
    { label: "Hoje", detail: "Visão geral do seu dia", path: "/hoje", icon: Sparkles },
    { label: "Tarefas", detail: "Planejar e acompanhar atividades", path: "/tarefas", icon: ListTodo },
    { label: "Agenda", detail: "Compromissos e lembretes", path: "/agenda", icon: CalendarDays },
    { label: "Memória", detail: "Revisar o que a A.R.A. sabe", path: "/memoria", icon: MemoryStick },
    { label: "Arquivos", detail: "Documentos e conhecimento", path: "/arquivos", icon: FileText },
    { label: "Projetos", detail: "Agrupar trabalho por contexto", path: "/projetos", icon: FolderKanban },
    { label: "Automações", detail: "Fluxos e rotinas inteligentes", path: "/automacoes", icon: Workflow },
    { label: "Integrações", detail: "Serviços conectados", path: "/integracoes", icon: Archive },
    { label: "Configurações", detail: "Preferências da A.R.A.", path: "/configuracoes", icon: Settings2 }
];

function CommandCenter({ aberto, onClose }) {
    const navigate = useNavigate();
    const [busca, setBusca] = useState("");
    const inputRef = useRef(null);

    useEffect(() => {
        if (!aberto) return;
        setBusca("");
        const timer = setTimeout(() => inputRef.current?.focus(), 30);
        return () => clearTimeout(timer);
    }, [aberto]);

    useEffect(() => {
        function onKeyDown(event) {
            if (event.key === "Escape" && aberto) onClose();
        }
        window.addEventListener("keydown", onKeyDown);
        return () => window.removeEventListener("keydown", onKeyDown);
    }, [aberto, onClose]);

    const filtrados = useMemo(() => {
        const termo = busca.trim().toLowerCase();
        if (!termo) return commands;
        return commands.filter((item) =>
            `${item.label} ${item.detail}`.toLowerCase().includes(termo)
        );
    }, [busca]);

    if (!aberto) return null;

    function abrir(path) {
        navigate(path);
        onClose();
    }

    return (
        <div className="command-overlay" onMouseDown={onClose}>
            <section className="command-center" onMouseDown={(event) => event.stopPropagation()}>
                <header className="command-search">
                    <Search size={19} />
                    <input
                        ref={inputRef}
                        value={busca}
                        onChange={(event) => setBusca(event.target.value)}
                        placeholder="Digite uma ação, módulo ou destino..."
                    />
                    <button type="button" onClick={onClose} aria-label="Fechar">
                        <X size={18} />
                    </button>
                </header>

                <div className="command-results">
                    <span className="command-eyebrow">A.R.A. COMMAND</span>
                    {filtrados.map(({ label, detail, path, icon: Icon }) => (
                        <button key={path} type="button" onClick={() => abrir(path)}>
                            <span className="command-icon"><Icon size={18} /></span>
                            <span>
                                <strong>{label}</strong>
                                <small>{detail}</small>
                            </span>
                            <kbd>↵</kbd>
                        </button>
                    ))}
                    {filtrados.length === 0 && (
                        <div className="command-empty">Nenhum comando encontrado.</div>
                    )}
                </div>
            </section>
        </div>
    );
}

export default CommandCenter;
