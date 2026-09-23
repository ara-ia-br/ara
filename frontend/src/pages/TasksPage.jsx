import {
    useCallback,
    useEffect,
    useMemo,
    useState
} from "react";

import {
    Check,
    CirclePlay,
    MoreHorizontal,
    Plus,
    RotateCcw,
    Trash2,
    X
} from "lucide-react";

import api from "../services/api";
import { useAuth } from "../context/AuthContext";


function TasksPage() {

    const { usuario } = useAuth();

    const [tarefas, setTarefas] = useState([]);

    const [filtro, setFiltro] = useState("TODAS");

    const [carregando, setCarregando] = useState(true);

    const [criando, setCriando] = useState(false);

    const [salvando, setSalvando] = useState(false);

    const [menuAberto, setMenuAberto] = useState(null);

    const [titulo, setTitulo] = useState("");
    const [descricao, setDescricao] = useState("");
    const [prioridade, setPrioridade] = useState(3);
    const [dataLimite, setDataLimite] = useState("");


    // =========================================================
    // CARREGAR TAREFAS
    // =========================================================

    const carregarTarefas = useCallback(
        async (mostrarCarregamento = true) => {

            if (!usuario?.id_usuario) {
                return;
            }

            if (mostrarCarregamento) {
                setCarregando(true);
            }

            try {

                const resposta = await api.get(
                    `/tarefas/usuario/${usuario.id_usuario}`,
                    {
                        params: {
                            _: Date.now()
                        }
                    }
                );

                setTarefas(
                    Array.isArray(resposta.data)
                        ? resposta.data
                        : []
                );

            } catch (erro) {

                console.error(
                    "Erro ao carregar tarefas:",
                    erro
                );

            } finally {

                if (mostrarCarregamento) {
                    setCarregando(false);
                }
            }
        },
        [usuario?.id_usuario]
    );


    // =========================================================
    // CRIAR TAREFA
    // =========================================================

    async function criarTarefa(event) {

        event.preventDefault();

        const tituloLimpo = titulo.trim();

        if (
            !tituloLimpo
            || salvando
        ) {
            return;
        }

        setSalvando(true);

        try {

            await api.post(
                "/tarefas",
                {
                    id_usuario:
                        usuario.id_usuario,

                    titulo:
                        tituloLimpo,

                    descricao:
                        descricao.trim()
                            ? descricao.trim()
                            : null,

                    prioridade:
                        Number(prioridade),

                    data_limite:
                        dataLimite
                            ? new Date(
                                dataLimite
                            ).toISOString()
                            : null
                }
            );

            // Busca novamente do banco.
            // Isso evita divergÃªncia entre frontend e backend.
            await carregarTarefas(false);

            limparFormulario();

            setCriando(false);

        } catch (erro) {

            console.error(
                "Erro ao criar tarefa:",
                erro
            );

            alert(
                erro.response?.data?.detail
                || "NÃ£o foi possÃ­vel criar a tarefa."
            );

        } finally {

            setSalvando(false);
        }
    }


    // =========================================================
    // INICIAR
    // =========================================================

    async function iniciarTarefa(
        idTarefa
    ) {

        try {

            const resposta = await api.patch(
                `/tarefas/${idTarefa}/iniciar`
            );

            atualizarTarefaLocal(
                resposta.data
            );

        } catch (erro) {

            console.error(
                "Erro ao iniciar tarefa:",
                erro
            );

            alert(
                erro.response?.data?.detail
                || "NÃ£o foi possÃ­vel iniciar a tarefa."
            );
        }
    }


    // =========================================================
    // CONCLUIR
    // =========================================================

    async function concluirTarefa(
        idTarefa
    ) {

        try {

            const resposta = await api.patch(
                `/tarefas/${idTarefa}/concluir`
            );

            atualizarTarefaLocal(
                resposta.data
            );

        } catch (erro) {

            console.error(
                "Erro ao concluir tarefa:",
                erro
            );

            alert(
                erro.response?.data?.detail
                || "NÃ£o foi possÃ­vel concluir a tarefa."
            );
        }
    }


    // =========================================================
    // CANCELAR
    // =========================================================

    async function cancelarTarefa(
        idTarefa
    ) {

        const confirmar = window.confirm(
            "Cancelar esta tarefa?"
        );

        if (!confirmar) {
            return;
        }

        try {

            const resposta = await api.patch(
                `/tarefas/${idTarefa}/cancelar`
            );

            atualizarTarefaLocal(
                resposta.data
            );

            setMenuAberto(null);

        } catch (erro) {

            console.error(
                "Erro ao cancelar tarefa:",
                erro
            );

            alert(
                erro.response?.data?.detail
                || "NÃ£o foi possÃ­vel cancelar a tarefa."
            );
        }
    }


    // =========================================================
    // REABRIR
    // =========================================================

    async function reabrirTarefa(
        tarefa
    ) {

        try {

            /*
             * Caso vocÃª ainda nÃ£o tenha criado
             * PATCH /tarefas/{id}/reabrir,
             * podemos adicionar depois.
             *
             * Por enquanto este botÃ£o sÃ³ serÃ¡ exibido
             * se vocÃª tiver esse endpoint.
             */

            const resposta = await api.patch(
                `/tarefas/${tarefa.id_tarefa}/reabrir`
            );

            atualizarTarefaLocal(
                resposta.data
            );

            setMenuAberto(null);

        } catch (erro) {

            console.error(
                "Erro ao reabrir tarefa:",
                erro
            );

            alert(
                erro.response?.data?.detail
                || "NÃ£o foi possÃ­vel reabrir a tarefa."
            );
        }
    }


    // =========================================================
    // EXCLUIR
    // =========================================================

    async function excluirTarefa(
        idTarefa
    ) {

        const confirmar = window.confirm(
            "Excluir esta tarefa definitivamente?"
        );

        if (!confirmar) {
            return;
        }

        try {

            await api.delete(
                `/tarefas/${idTarefa}`
            );

            setTarefas(
                (anteriores) =>
                    anteriores.filter(
                        (tarefa) =>
                            tarefa.id_tarefa
                            !== idTarefa
                    )
            );

            setMenuAberto(null);

        } catch (erro) {

            console.error(
                "Erro ao excluir tarefa:",
                erro
            );

            alert(
                erro.response?.data?.detail
                || "NÃ£o foi possÃ­vel excluir a tarefa."
            );
        }
    }


    // =========================================================
    // ATUALIZA UMA TAREFA LOCALMENTE
    // =========================================================

    function atualizarTarefaLocal(
        tarefaAtualizada
    ) {

        if (!tarefaAtualizada?.id_tarefa) {
            return;
        }

        setTarefas(
            (anteriores) =>
                anteriores.map(
                    (tarefa) =>
                        tarefa.id_tarefa
                        === tarefaAtualizada.id_tarefa

                            ? tarefaAtualizada

                            : tarefa
                )
        );
    }


    // =========================================================
    // LIMPAR FORMULÃRIO
    // =========================================================

    function limparFormulario() {

        setTitulo("");
        setDescricao("");
        setPrioridade(3);
        setDataLimite("");
    }


    function fecharModal() {

        if (salvando) {
            return;
        }

        limparFormulario();

        setCriando(false);
    }


    // =========================================================
    // FORMATAR DATA
    // =========================================================

    function formatarData(
        data
    ) {

        if (!data) {
            return "Sem prazo";
        }

        const valor = new Date(data);

        if (
            Number.isNaN(
                valor.getTime()
            )
        ) {
            return "Data invÃ¡lida";
        }

        return valor.toLocaleString(
            "pt-BR",
            {
                day: "2-digit",
                month: "2-digit",
                year: "numeric",
                hour: "2-digit",
                minute: "2-digit"
            }
        );
    }


    // =========================================================
    // FORMATAR STATUS
    // =========================================================

    function formatarStatus(
        status
    ) {

        switch (status) {

            case "PENDENTE":
                return "Pendente";

            case "EM_ANDAMENTO":
                return "Em andamento";

            case "CONCLUIDA":
                return "ConcluÃ­da";

            case "CANCELADA":
                return "Cancelada";

            default:
                return status;
        }
    }


    // =========================================================
    // FILTROS
    // =========================================================

    const tarefasFiltradas = useMemo(
        () => {

            if (filtro === "TODAS") {
                return tarefas;
            }

            return tarefas.filter(
                (tarefa) =>
                    tarefa.status === filtro
            );

        },
        [
            tarefas,
            filtro
        ]
    );


    // =========================================================
    // CARREGAMENTO INICIAL + SINCRONIZAÃ‡ÃƒO
    // =========================================================

    useEffect(
        () => {

            carregarTarefas();


            // Quando o Chat informar que uma tool
            // de tarefa foi executada.
            function tarefasAtualizadas() {

                carregarTarefas(false);
            }


            // Quando o usuÃ¡rio volta para a janela.
            function janelaFocada() {

                carregarTarefas(false);
            }


            // Quando troca de aba e volta.
            function visibilidadeMudou() {

                if (
                    document.visibilityState
                    === "visible"
                ) {

                    carregarTarefas(false);
                }
            }


            window.addEventListener(
                "ara:tarefas-atualizadas",
                tarefasAtualizadas
            );

            window.addEventListener(
                "focus",
                janelaFocada
            );

            document.addEventListener(
                "visibilitychange",
                visibilidadeMudou
            );


            return () => {

                window.removeEventListener(
                    "ara:tarefas-atualizadas",
                    tarefasAtualizadas
                );

                window.removeEventListener(
                    "focus",
                    janelaFocada
                );

                document.removeEventListener(
                    "visibilitychange",
                    visibilidadeMudou
                );
            };

        },
        [
            carregarTarefas
        ]
    );


    return (
        <main className="tasks-page">

            {/* =================================================
                CABEÃ‡ALHO
            ================================================= */}

            <header className="tasks-header">

                <div>

                    <h1>
                        Tarefas
                    </h1>

                    <p>
                        Organize suas atividades
                        e acompanhe seu progresso.
                    </p>

                </div>


                <button
                    className="task-create-button"
                    onClick={
                        () =>
                            setCriando(true)
                    }
                >

                    <Plus size={18} />

                    Nova tarefa

                </button>

            </header>


            <section className="tasks-content">

                {/* =================================================
                    FILTROS
                ================================================= */}

                <div className="task-filters">

                    {
                        [
                            [
                                "TODAS",
                                "Todas"
                            ],
                            [
                                "PENDENTE",
                                "Pendentes"
                            ],
                            [
                                "EM_ANDAMENTO",
                                "Em andamento"
                            ],
                            [
                                "CONCLUIDA",
                                "ConcluÃ­das"
                            ],
                            [
                                "CANCELADA",
                                "Canceladas"
                            ]
                        ].map(
                            ([valor, texto]) => (

                                <button
                                    key={valor}
                                    className={
                                        filtro === valor

                                            ? "task-filter active"

                                            : "task-filter"
                                    }
                                    onClick={
                                        () =>
                                            setFiltro(
                                                valor
                                            )
                                    }
                                >

                                    {texto}

                                </button>

                            )
                        )
                    }

                </div>


                {/* =================================================
                    CARREGANDO
                ================================================= */}

                {
                    carregando
                    && (
                        <div className="task-empty">

                            Carregando tarefas...

                        </div>
                    )
                }


                {/* =================================================
                    SEM RESULTADOS
                ================================================= */}

                {
                    !carregando
                    && tarefasFiltradas.length === 0
                    && (
                        <div className="task-empty">

                            Nenhuma tarefa encontrada.

                        </div>
                    )
                }


                {/* =================================================
                    LISTA
                ================================================= */}

                {
                    !carregando
                    && (
                        <div className="task-list">

                            {
                                tarefasFiltradas.map(
                                    (tarefa) => (

                                        <article
                                            key={
                                                tarefa.id_tarefa
                                            }
                                            className="task-card"
                                        >

                                            <div className="task-card-top">

                                                <div>

                                                    <div className="task-title-row">

                                                        <h3>
                                                            {tarefa.titulo}
                                                        </h3>


                                                        <span
                                                            className={
                                                                `task-priority priority-${tarefa.prioridade}`
                                                            }
                                                        >

                                                            Prioridade {
                                                                tarefa.prioridade
                                                            }

                                                        </span>

                                                    </div>


                                                    {
                                                        tarefa.descricao
                                                        && (
                                                            <p className="task-description">

                                                                {
                                                                    tarefa.descricao
                                                                }

                                                            </p>
                                                        )
                                                    }

                                                </div>


                                                {/* MENU */}

                                                <div className="task-menu-container">

                                                    <button
                                                        className="task-menu-button"
                                                        onClick={
                                                            () =>
                                                                setMenuAberto(
                                                                    menuAberto
                                                                    === tarefa.id_tarefa

                                                                        ? null

                                                                        : tarefa.id_tarefa
                                                                )
                                                        }
                                                    >

                                                        <MoreHorizontal
                                                            size={19}
                                                        />

                                                    </button>


                                                    {
                                                        menuAberto
                                                        === tarefa.id_tarefa
                                                        && (
                                                            <div className="task-menu">

                                                                {
                                                                    tarefa.status
                                                                    !== "CONCLUIDA"
                                                                    && tarefa.status
                                                                    !== "CANCELADA"
                                                                    && (
                                                                        <button
                                                                            onClick={
                                                                                () =>
                                                                                    cancelarTarefa(
                                                                                        tarefa.id_tarefa
                                                                                    )
                                                                            }
                                                                        >

                                                                            <X
                                                                                size={15}
                                                                            />

                                                                            Cancelar

                                                                        </button>
                                                                    )
                                                                }


                                                                {
                                                                    (
                                                                        tarefa.status
                                                                        === "CONCLUIDA"

                                                                        || tarefa.status
                                                                        === "CANCELADA"
                                                                    )
                                                                    && (
                                                                        <button
                                                                            onClick={
                                                                                () =>
                                                                                    reabrirTarefa(
                                                                                        tarefa
                                                                                    )
                                                                            }
                                                                        >

                                                                            <RotateCcw
                                                                                size={15}
                                                                            />

                                                                            Reabrir

                                                                        </button>
                                                                    )
                                                                }


                                                                <button
                                                                    className="danger"
                                                                    onClick={
                                                                        () =>
                                                                            excluirTarefa(
                                                                                tarefa.id_tarefa
                                                                            )
                                                                    }
                                                                >

                                                                    <Trash2
                                                                        size={15}
                                                                    />

                                                                    Excluir

                                                                </button>

                                                            </div>
                                                        )
                                                    }

                                                </div>

                                            </div>


                                            {/* META */}

                                            <div className="task-meta">

                                                <span>

                                                    Status:{" "}

                                                    <strong>
                                                        {
                                                            formatarStatus(
                                                                tarefa.status
                                                            )
                                                        }
                                                    </strong>

                                                </span>


                                                <span>

                                                    Prazo:{" "}

                                                    <strong>
                                                        {
                                                            formatarData(
                                                                tarefa.data_limite
                                                            )
                                                        }
                                                    </strong>

                                                </span>

                                            </div>


                                            {/* AÃ‡Ã•ES */}

                                            <div className="task-actions">

                                                {
                                                    tarefa.status
                                                    === "PENDENTE"
                                                    && (
                                                        <button
                                                            onClick={
                                                                () =>
                                                                    iniciarTarefa(
                                                                        tarefa.id_tarefa
                                                                    )
                                                            }
                                                        >

                                                            <CirclePlay
                                                                size={16}
                                                            />

                                                            Iniciar

                                                        </button>
                                                    )
                                                }


                                                {
                                                    (
                                                        tarefa.status
                                                        === "PENDENTE"

                                                        || tarefa.status
                                                        === "EM_ANDAMENTO"
                                                    )
                                                    && (
                                                        <button
                                                            className="primary"
                                                            onClick={
                                                                () =>
                                                                    concluirTarefa(
                                                                        tarefa.id_tarefa
                                                                    )
                                                            }
                                                        >

                                                            <Check
                                                                size={16}
                                                            />

                                                            Concluir

                                                        </button>
                                                    )
                                                }


                                                {
                                                    tarefa.status
                                                    === "CONCLUIDA"
                                                    && (
                                                        <span className="task-finished">

                                                            <Check
                                                                size={16}
                                                            />

                                                            ConcluÃ­da

                                                        </span>
                                                    )
                                                }


                                                {
                                                    tarefa.status
                                                    === "CANCELADA"
                                                    && (
                                                        <span className="task-cancelled">

                                                            Cancelada

                                                        </span>
                                                    )
                                                }

                                            </div>

                                        </article>

                                    )
                                )
                            }

                        </div>
                    )
                }

            </section>


            {/* =================================================
                MODAL NOVA TAREFA
            ================================================= */}

            {
                criando
                && (
                    <div
                        className="task-modal-overlay"
                        onMouseDown={
                            fecharModal
                        }
                    >

                        <form
                            className="task-modal"
                            onSubmit={
                                criarTarefa
                            }
                            onMouseDown={
                                (event) =>
                                    event.stopPropagation()
                            }
                        >

                            <div className="task-modal-header">

                                <div>

                                    <h2>
                                        Nova tarefa
                                    </h2>

                                    <p>
                                        Adicione uma nova atividade.
                                    </p>

                                </div>


                                <button
                                    type="button"
                                    onClick={
                                        fecharModal
                                    }
                                    disabled={
                                        salvando
                                    }
                                >

                                    <X size={20} />

                                </button>

                            </div>


                            <label>

                                TÃ­tulo

                                <input
                                    type="text"
                                    value={titulo}
                                    onChange={
                                        (event) =>
                                            setTitulo(
                                                event.target.value
                                            )
                                    }
                                    maxLength={200}
                                    autoFocus
                                    required
                                />

                            </label>


                            <label>

                                DescriÃ§Ã£o

                                <textarea
                                    value={descricao}
                                    onChange={
                                        (event) =>
                                            setDescricao(
                                                event.target.value
                                            )
                                    }
                                    rows={4}
                                />

                            </label>


                            <div className="task-form-row">

                                <label>

                                    Prioridade

                                    <select
                                        value={prioridade}
                                        onChange={
                                            (event) =>
                                                setPrioridade(
                                                    Number(
                                                        event.target.value
                                                    )
                                                )
                                        }
                                    >

                                        <option value={1}>
                                            1 - Muito baixa
                                        </option>

                                        <option value={2}>
                                            2 - Baixa
                                        </option>

                                        <option value={3}>
                                            3 - Normal
                                        </option>

                                        <option value={4}>
                                            4 - Alta
                                        </option>

                                        <option value={5}>
                                            5 - Urgente
                                        </option>

                                    </select>

                                </label>


                                <label>

                                    Prazo

                                    <input
                                        type="datetime-local"
                                        value={
                                            dataLimite
                                        }
                                        onChange={
                                            (event) =>
                                                setDataLimite(
                                                    event.target.value
                                                )
                                        }
                                    />

                                </label>

                            </div>


                            <div className="task-modal-actions">

                                <button
                                    type="button"
                                    onClick={
                                        fecharModal
                                    }
                                    disabled={
                                        salvando
                                    }
                                >

                                    Cancelar

                                </button>


                                <button
                                    type="submit"
                                    className="primary"
                                    disabled={
                                        salvando
                                        || !titulo.trim()
                                    }
                                >

                                    <Plus size={17} />

                                    {
                                        salvando
                                            ? "Criando..."
                                            : "Criar tarefa"
                                    }

                                </button>

                            </div>

                        </form>

                    </div>
                )
            }

        </main>
    );
}


export default TasksPage;
