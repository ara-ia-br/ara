import {
    useEffect,
    useRef,
    useState
} from "react";

import {
    ArrowUp,
    Mic,
    Paperclip
} from "lucide-react";

import api from "../services/api";
import Message from "./Message";


function Chat({
    conversaSelecionada,
    conversaCriada
}) {

    const [mensagem, setMensagem] = useState("");

    const [mensagens, setMensagens] = useState([]);

    const [carregando, setCarregando] = useState(false);

    const fimMensagensRef = useRef(null);


    // =========================================================
    // CARREGAR HISTÓRICO
    // =========================================================

    async function carregarHistorico() {

        if (!conversaSelecionada) {

            setMensagens([]);

            return;
        }


        try {

            const resposta = await api.get(
                `/mensagens/conversa/${conversaSelecionada.id_conversa}`
            );


            const mensagensConvertidas = (
                resposta.data.map(
                    (item) => ({
                        id: item.id_mensagem,

                        autor:
                            item.remetente === "JARVIS"
                                ? "jarvis"
                                : "user",

                        conteudo: item.conteudo
                    })
                )
            );


            setMensagens(
                mensagensConvertidas
            );


        } catch (erro) {

            console.error(
                "Erro ao carregar histórico:",
                erro
            );
        }
    }


    // =========================================================
    // ENVIAR MENSAGEM
    // =========================================================

    async function enviarMensagem() {

        const texto = mensagem.trim();


        if (
            !texto
            || carregando
            || !conversaSelecionada
        ) {
            return;
        }


        // =====================================================
        // MENSAGEM TEMPORÁRIA DO USUÁRIO
        // =====================================================

        const mensagemUsuario = {

            id:
                `temp-${Date.now()}`,

            autor:
                "user",

            conteudo:
                texto
        };


        setMensagens(
            (anteriores) => [
                ...anteriores,
                mensagemUsuario
            ]
        );


        setMensagem("");

        setCarregando(true);


        try {

            // =================================================
            // POST /CHAT
            // =================================================

            const resposta = await api.post(
                "/chat",
                {
                    id_conversa:
                        conversaSelecionada.id_conversa,

                    mensagem:
                        texto
                }
            );


            console.log(
                "===== RESPOSTA /CHAT =====",
                resposta.data
            );


            // =================================================
            // VALIDA RESPOSTA DO BACKEND
            // =================================================

            const respostaJarvis = (
                resposta.data
                    ?.resposta_jarvis
            );


            if (
                !respostaJarvis
                || typeof respostaJarvis
                !== "string"
            ) {

                console.error(
                    "Resposta inválida do backend:",
                    resposta.data
                );


                throw new Error(
                    "O backend não retornou resposta_jarvis."
                );
            }


            // =================================================
            // MOSTRA RESPOSTA PRIMEIRO
            // =================================================

            const mensagemJarvis = {

                id:
                    `jarvis-${Date.now()}`,

                autor:
                    "jarvis",

                conteudo:
                    respostaJarvis
            };


            setMensagens(
                (anteriores) => [
                    ...anteriores,
                    mensagemJarvis
                ]
            );


            // =================================================
            // FERRAMENTA EXECUTADA
            // =================================================

            const ferramenta = (
                resposta.data
                    ?.ferramenta
            );


            // =================================================
            // NOTIFICA PÁGINA DE TAREFAS
            //
            // Isso não pode derrubar o chat.
            // =================================================

            if (
                ferramenta
                && typeof ferramenta === "string"
                && ferramenta.includes(
                    "tarefa"
                )
            ) {

                try {

                    window.dispatchEvent(
                        new CustomEvent(
                            "jarvis:tarefas-atualizadas",
                            {
                                detail: {
                                    ferramenta
                                }
                            }
                        )
                    );


                } catch (
                    erroEvento
                ) {

                    console.error(
                        "Erro ao disparar atualização de tarefas:",
                        erroEvento
                    );
                }
            }


            // =================================================
            // ATUALIZA LISTA DE CONVERSAS
            //
            // IMPORTANTE:
            // ocorre SOMENTE depois de mostrar
            // a resposta do JARVIS.
            // =================================================

            if (
                typeof conversaCriada
                === "function"
            ) {

                try {

                    await conversaCriada();


                } catch (
                    erroConversa
                ) {

                    console.error(
                        "Erro ao atualizar conversas:",
                        erroConversa
                    );
                }
            }


        } catch (erro) {

            // =================================================
            // DEBUG COMPLETO
            // =================================================

            console.error(
                "================================="
            );

            console.error(
                "ERRO AO ENVIAR MENSAGEM"
            );

            console.error(
                "Mensagem:",
                erro?.message
            );

            console.error(
                "Código:",
                erro?.code
            );

            console.error(
                "Status:",
                erro?.response?.status
            );

            console.error(
                "Resposta backend:",
                erro?.response?.data
            );

            console.error(
                "Erro completo:",
                erro
            );

            console.error(
                "================================="
            );


            // =================================================
            // MENSAGEM DE ERRO
            // =================================================

            const detalheBackend = (
                erro
                    ?.response
                    ?.data
                    ?.detail
            );


            const mensagemErro = {

                id:
                    `erro-${Date.now()}`,

                autor:
                    "jarvis",

                conteudo:
                    detalheBackend
                    || (
                        "Deu ruim por aqui. "
                        + "Não consegui responder agora."
                    )
            };


            setMensagens(
                (anteriores) => [
                    ...anteriores,
                    mensagemErro
                ]
            );


        } finally {

            setCarregando(false);
        }
    }


    // =========================================================
    // ENTER PARA ENVIAR
    // =========================================================

    function verificarEnter(
        event
    ) {

        if (
            event.key === "Enter"
            && !event.shiftKey
        ) {

            event.preventDefault();

            enviarMensagem();
        }
    }


    // =========================================================
    // CARREGAR HISTÓRICO AO TROCAR DE CONVERSA
    // =========================================================

    useEffect(
        () => {

            carregarHistorico();

        },
        [
            conversaSelecionada
                ?.id_conversa
        ]
    );


    // =========================================================
    // AUTO SCROLL
    // =========================================================

    useEffect(
        () => {

            fimMensagensRef
                .current
                ?.scrollIntoView(
                    {
                        behavior:
                            "smooth"
                    }
                );

        },
        [
            mensagens,
            carregando
        ]
    );


    // =========================================================
    // SEM CONVERSA
    // =========================================================

    if (!conversaSelecionada) {

        return (

            <main className="chat">

                <div
                    className="welcome"
                    style={{
                        margin: "auto"
                    }}
                >

                    <div
                        className="jarvis-symbol"
                    >
                        J
                    </div>


                    <h2>
                        Bem-vindo ao JARVIS
                    </h2>


                    <p>
                        Crie uma conversa
                        para começar.
                    </p>

                </div>

            </main>
        );
    }


    // =========================================================
    // CHAT
    // =========================================================

    return (

        <main className="chat">

            {/* =================================================
                HEADER
            ================================================= */}

            <header className="chat-header">

                <div>

                    <h2>
                        {
                            conversaSelecionada
                                .titulo
                        }
                    </h2>


                    <span className="online">

                        <span
                            className="online-dot"
                        />

                        JARVIS Online

                    </span>

                </div>

            </header>


            {/* =================================================
                MENSAGENS
            ================================================= */}

            <section className="messages">

                {
                    mensagens.length === 0
                    && (

                        <div className="welcome">

                            <div
                                className="jarvis-symbol"
                            >
                                J
                            </div>


                            <h2>
                                E aí! O que vamos
                                fazer hoje?
                            </h2>


                            <p>
                                Converse, pergunte ou
                                peça para eu fazer
                                alguma coisa.
                            </p>

                        </div>
                    )
                }


                {
                    mensagens.map(
                        (item) => (

                            <Message
                                key={
                                    item.id
                                }
                                autor={
                                    item.autor
                                }
                            >

                                {
                                    item.conteudo
                                }

                            </Message>

                        )
                    )
                }


                {/* =================================================
                    INDICADOR DE DIGITAÇÃO
                ================================================= */}

                {
                    carregando
                    && (

                        <div
                            className="
                                message
                                jarvis-message
                            "
                        >

                            <div
                                className="
                                    message-author
                                "
                            >
                                JARVIS
                            </div>


                            <div className="typing">

                                <span />
                                <span />
                                <span />

                            </div>

                        </div>
                    )
                }


                <div
                    ref={
                        fimMensagensRef
                    }
                />

            </section>


            {/* =================================================
                COMPOSER
            ================================================= */}

            <div className="composer-container">

                <div className="composer">

                    {/* ANEXO */}

                    <button
                        type="button"
                        className="
                            composer-button
                        "
                        disabled={
                            carregando
                        }
                    >

                        <Paperclip
                            size={20}
                        />

                    </button>


                    {/* TEXTO */}

                    <textarea
                        value={
                            mensagem
                        }
                        onChange={
                            (event) =>
                                setMensagem(
                                    event
                                        .target
                                        .value
                                )
                        }
                        onKeyDown={
                            verificarEnter
                        }
                        placeholder={
                            carregando
                                ? (
                                    "JARVIS está "
                                    + "pensando..."
                                )
                                : (
                                    "Pergunte "
                                    + "alguma coisa..."
                                )
                        }
                        disabled={
                            carregando
                        }
                        rows={1}
                    />


                    {/* MICROFONE */}

                    <button
                        type="button"
                        className="
                            composer-button
                        "
                        disabled={
                            carregando
                        }
                    >

                        <Mic
                            size={20}
                        />

                    </button>


                    {/* ENVIAR */}

                    <button
                        type="button"
                        className="
                            send-button
                        "
                        onClick={
                            enviarMensagem
                        }
                        disabled={
                            carregando
                            || !mensagem.trim()
                        }
                    >

                        <ArrowUp
                            size={21}
                        />

                    </button>

                </div>


                <span className="disclaimer">

                    JARVIS pode cometer erros.
                    Verifique informações
                    importantes.

                </span>

            </div>

        </main>
    );
}


export default Chat;