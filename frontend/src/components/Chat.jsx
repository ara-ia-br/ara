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

import "../chat-modern.css";

import araChatLogo
    from "../assets/brand/logo-chat.png";

import useUserLocation from "../hooks/useUserLocation";


function calcularDistanciaMetros(
    lat1,
    lon1,
    lat2,
    lon2
) {

    const raioTerra = 6371000;

    const paraRadianos = (
        valor
    ) => (
        valor * Math.PI / 180
    );


    const deltaLat = paraRadianos(
        lat2 - lat1
    );

    const deltaLon = paraRadianos(
        lon2 - lon1
    );


    const a = (
        Math.sin(deltaLat / 2) ** 2
        + Math.cos(
            paraRadianos(lat1)
        )
        * Math.cos(
            paraRadianos(lat2)
        )
        * Math.sin(deltaLon / 2) ** 2
    );


    const c = (
        2 * Math.atan2(
            Math.sqrt(a),
            Math.sqrt(1 - a)
        )
    );


    return raioTerra * c;
}


function Chat({
    conversaSelecionada,
    conversaCriada
}) {

    const [mensagem, setMensagem] = useState("");

    const [mensagens, setMensagens] = useState([]);

    const [carregando, setCarregando] = useState(false);

    const fimMensagensRef = useRef(null);

    const rotaAtivaRef = useRef(null);

    const recalculoRotaEmAndamentoRef =
    useRef(false);

    const {
    location,
    error: locationError,
    tracking: locationTracking,
    startTracking,
    stopTracking,
    getCurrentLocation
} = useUserLocation();


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
                item.remetente === "ARA"
                    ? "ara"
                    : "user",

            conteudo:
                item.conteudo,

            visualizacao:
                item.visualizacao
                || null
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


   function mensagemUsaLocalizacao(
    texto
) {

    const normalizado = (
        String(texto || "")
            .toLowerCase()
    );

    return (
        /\bdaqui\b/.test(normalizado)
        || /\bonde (?:eu )?estou\b/.test(normalizado)
        || /\bminha localização\b/.test(normalizado)
        || /\bminha localizacao\b/.test(normalizado)
        || /\blocalização atual\b/.test(normalizado)
        || /\blocalizacao atual\b/.test(normalizado)
        || /\bem que bairro (?:eu )?estou\b/.test(normalizado)
        || /\bem que cidade (?:eu )?estou\b/.test(normalizado)
    );
}


// =========================================================
// CONTROLE DE LOCALIZAÇÃO
// =========================================================

function alternarLocalizacao() {

    if (locationTracking) {

        stopTracking();
        return;
    }

    startTracking();
}

    // =========================================================
    // ENVIAR MENSAGEM
    // =========================================================

    async function enviarMensagem() {

        const texto = mensagem.trim();


        let localizacaoAtual = null;




if (
    mensagemUsaLocalizacao(texto)
) {

    if (
        !locationTracking
        || !location
    ) {

        setMensagens(
            (anteriores) => [
                ...anteriores,
                {
                    id:
                        `localizacao-${Date.now()}`,

                    autor:
                        "ara",

                    conteudo:
                        (
                            "Para usar sua localização atual, "
                            + "ative a localização no botão "
                            + "acima do chat."
                        )
                }
            ]
        );

        return;
    }


    localizacaoAtual =
        location;
}

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
        texto,

    localizacao:
       localizacaoAtual
}
            );


            console.log(
                "===== RESPOSTA /CHAT =====",
                resposta.data
            );


            // =================================================
            // VALIDA RESPOSTA DO BACKEND
            // =================================================

            const respostaAra = (
                resposta.data
                    ?.resposta_ara
            );


            if (
                !respostaAra
                || typeof respostaAra
                !== "string"
            ) {

                console.error(
                    "Resposta inválida do backend:",
                    resposta.data
                );


                throw new Error(
                    "O backend não retornou resposta_ara."
                );
            }


            // =================================================
            // MOSTRA RESPOSTA PRIMEIRO
            // =================================================

           const mensagemAra = {
             id:
                    `ara-${Date.now()}`,

                autor:
                    "ara",

                conteudo:
                    respostaAra,

                visualizacao:
                    resposta.data
                        ?.visualizacao
                        || null
            };



            setMensagens(
                (anteriores) => [
                    ...anteriores,
                    mensagemAra
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
                            "ara:tarefas-atualizadas",
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
            // a resposta da A.R.A..
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
                    "ara",

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
// ROTA GPS ATIVA
// =========================================================

useEffect(
    () => {

        const ultimaRota = (
            [...mensagens]
                .reverse()
                .find(
                    (item) =>
                        item.autor === "ara"
                        && item.visualizacao
                            ?.tipo === "rota"
                )
        );


        if (!ultimaRota) {

            rotaAtivaRef.current = null;

            return;
        }


        const visualizacao =
            ultimaRota.visualizacao;


        const origem =
            visualizacao?.origem;


        /*
         * Só rotas iniciadas pela localização
         * atual devem ser recalculadas.
         *
         * Rotas:
         * Centro -> Copacabana
         *
         * não entram aqui.
         */
        if (
            origem?.nome
            !== "Sua localização atual"
        ) {

            rotaAtivaRef.current = null;

            return;
        }


        const latitude = Number(
            origem.latitude
        );

        const longitude = Number(
            origem.longitude
        );


        const destino = (
            visualizacao
                ?.destino
                ?.consulta
            || visualizacao
                ?.destino
                ?.nome
        );


        if (
            !Number.isFinite(latitude)
            || !Number.isFinite(longitude)
            || !destino
        ) {

            rotaAtivaRef.current = null;

            return;
        }


        /*
         * Não reinicia o relógio cada vez
         * que o card é atualizado.
         */
        if (
            rotaAtivaRef.current
                ?.idMensagem
            === ultimaRota.id
        ) {
            return;
        }


        rotaAtivaRef.current = {

            idMensagem:
                ultimaRota.id,

            destino,

            latitude,

            longitude,

            ultimaAtualizacao:
                Date.now()
        };

    },
    [
        mensagens
    ]
);

// =========================================================
// RECÁLCULO INTELIGENTE DE ROTA
// =========================================================

useEffect(
    () => {

        if (
            !locationTracking
            || !location
        ) {
            return;
        }


        const rota =
            rotaAtivaRef.current;


        if (!rota) {
            return;
        }


        if (
            recalculoRotaEmAndamentoRef
                .current
        ) {
            return;
        }


        const latitudeAtual = Number(
            location.latitude
        );

        const longitudeAtual = Number(
            location.longitude
        );


        if (
            !Number.isFinite(
                latitudeAtual
            )
            || !Number.isFinite(
                longitudeAtual
            )
        ) {
            return;
        }


        const distanciaPercorrida = (
            calcularDistanciaMetros(
                rota.latitude,
                rota.longitude,
                latitudeAtual,
                longitudeAtual
            )
        );


        const tempoDecorrido = (
            Date.now()
            - rota.ultimaAtualizacao
        );


        // Mínimo: 150 metros.
        if (
            distanciaPercorrida
            < 150
        ) {
            return;
        }


        // Mínimo: 30 segundos.
        if (
            tempoDecorrido
            < 30000
        ) {
            return;
        }


        recalculoRotaEmAndamentoRef
            .current = true;


        api.post(
            "/chat/rota/recalcular",
            {
                destino:
                    rota.destino,

                latitude:
                    latitudeAtual,

                longitude:
                    longitudeAtual
            }
        )
            .then(
                (resposta) => {

                    const novaVisualizacao = (
                        resposta.data
                            ?.visualizacao
                    );


                    const novaResposta = (
                        resposta.data
                            ?.resposta_ara
                    );


                    if (
                        !novaVisualizacao
                    ) {
                        return;
                    }


                    /*
                     * Atualiza a mensagem existente.
                     * Não cria outra mensagem.
                     */
                    setMensagens(
                        (anteriores) =>
                            anteriores.map(
                                (item) => {

                                    if (
                                        item.id
                                        !== rota.idMensagem
                                    ) {
                                        return item;
                                    }


                                    return {
                                        ...item,

                                        conteudo:
                                            (
                                                typeof novaResposta
                                                === "string"
                                            )
                                                ? novaResposta
                                                : item.conteudo,

                                        visualizacao:
                                            novaVisualizacao
                                    };
                                }
                            )
                    );


                    /*
                     * A nova posição vira a referência
                     * para o próximo deslocamento.
                     */
                    rotaAtivaRef.current = {
                        ...rota,

                        latitude:
                            latitudeAtual,

                        longitude:
                            longitudeAtual,

                        destino:
                            (
                                novaVisualizacao
                                    ?.destino
                                    ?.consulta
                                || rota.destino
                            ),

                        ultimaAtualizacao:
                            Date.now()
                    };


                    console.log(
                        "[ROTA] Recalculada:",
                        {
                            distanciaPercorrida:
                                Math.round(
                                    distanciaPercorrida
                                ),

                            destino:
                                rota.destino
                        }
                    );
                }
            )
            .catch(
                (erro) => {

                    console.error(
                        "[ROTA] Erro ao recalcular:",
                        erro
                    );
                }
            )
            .finally(
                () => {

                    recalculoRotaEmAndamentoRef
                        .current = false;
                }
            );

    },
    [
        location,
        locationTracking
    ]
);




       // =========================================================
    // SEM CONVERSA
    // =========================================================

    if (!conversaSelecionada) {
        return (
            <main className="chat ara-chat-shell">

                <div className="ara-empty-state">

                    <div className="ara-brand-badge">
                        A
                    </div>

                    <span className="ara-eyebrow">
                        ASSISTENTE DE RACIOCÍNIO ADAPTATIVO
                    </span>

                    <h1 className="ara-empty-title">
                        Sua próxima ideia
                        <span> começa aqui.</span>
                    </h1>

                    <p className="ara-empty-description">
                        Crie uma nova conversa para começar.
                    </p>

                </div>

            </main>
        );
    }


    // =========================================================
    // CHAT
    // =========================================================

    return (

        <main className="chat ara-chat-shell">

            {/* =================================================
                HEADER
            ================================================= */}

            <header className="ara-chat-header">

                <div className="ara-chat-header-content">

                    <div>

                        <span className="ara-chat-label">
                            CONVERSA
                        </span>

                        <h2>
                            {conversaSelecionada.titulo}
                        </h2>

                    </div>


                    <div className="ara-online-status">

                        <span className="ara-online-dot" />

                        <span>
                            A.R.A. Online
                        </span>

                    </div>


                    <button
    type="button"
    className={
        "ara-location-status "
        + (
            locationTracking
                ? "is-active"
                : ""
        )
    }
    onClick={alternarLocalizacao}
    title={
        locationTracking
            ? "Desativar localização"
            : "Ativar localização"
    }
>
    <span
        className="ara-location-status-dot"
    />

    <span>
    {
        locationTracking
            ? (
                location?.accuracy
                    ? (
                        "Localização ativa"
                        + " · ±"
                        + Math.round(
                            location.accuracy
                        )
                        + " m"
                    )
                    : "Localização ativa"
            )
            : "Localização desativada"
    }
</span>
</button>

                    {
    locationError
    && (
        <span
            className="ara-location-error"
            title={locationError}
        >
            Localização indisponível
        </span>
    )
}

                </div>

            </header>


            {/* =================================================
                MENSAGENS
            ================================================= */}

            <section
                className={
                    mensagens.length === 0
                        ? "messages ara-messages ara-messages-empty"
                        : "messages ara-messages"
                }
            >

                {
                    mensagens.length === 0
                    && (

                        <div className="ara-welcome">

                            <div className="ara-welcome-symbol">
                                A
                            </div>


                            <span className="ara-eyebrow">
                                O PRÓXIMO PASSO É O FUTURO
                            </span>


                            <h1 className="ara-welcome-title">

                                E aí! O que vamos

                                <span>
                                    fazer hoje?
                                </span>

                            </h1>


                            <p className="ara-welcome-description">
                                Converse, pergunte ou peça para a A.R.A.
                                fazer alguma coisa.
                            </p>


                            <div className="ara-suggestions">

                                <button
                                    type="button"
                                    onClick={() =>
                                        setMensagem(
                                            "Me ajude a organizar meu dia"
                                        )
                                    }
                                >
                                    <span>
                                        Organizar meu dia
                                    </span>

                                    <small>
                                        Tarefas e prioridades
                                    </small>
                                </button>


                                <button
                                    type="button"
                                    onClick={() =>
                                        setMensagem(
                                            "Quero entender um assunto"
                                        )
                                    }
                                >
                                    <span>
                                        Aprender algo
                                    </span>

                                    <small>
                                        Explicações do seu jeito
                                    </small>
                                </button>


                                <button
                                    type="button"
                                    onClick={() =>
                                        setMensagem(
                                            "Crie uma tarefa para mim"
                                        )
                                    }
                                >
                                    <span>
                                        Criar uma tarefa
                                    </span>

                                    <small>
                                        Organize algo rapidamente
                                    </small>
                                </button>


                                <button
                                    type="button"
                                    onClick={() =>
                                        setMensagem(
                                            "Me ajude a planejar algo"
                                        )
                                    }
                                >
                                    <span>
                                        Planejar algo
                                    </span>

                                    <small>
                                        Ideias, planos e próximos passos
                                    </small>
                                </button>

                            </div>

                        </div>
                    )
                }


                {
                    mensagens.map(
                        (item) => (

                            <Message
                                key={item.id}
                                autor={item.autor}
                                visualizacao={
                                    item.visualizacao
                                }
                            >
                                {item.conteudo}
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

                        <div className="message ara-message">
                            <div className="message-author">

                                <span className="message-avatar ara-avatar">
                                    <img
                                        src={araChatLogo}
                                        alt=""
                                        aria-hidden="true"
                                    />
                                </span>

                                <span>
                                    A.R.A.
                                </span>

                            </div>


                            <div className="typing">

                                <span />
                                <span />
                                <span />

                            </div>

                        </div>
                    )
                }


                <div ref={fimMensagensRef} />

            </section>


            {/* =================================================
                COMPOSER
            ================================================= */}

            <div className="ara-composer-area">

                <div className="ara-composer">

                    <button
                        type="button"
                        className="ara-composer-action"
                        disabled={carregando}
                        title="Anexar arquivo"
                    >
                        <Paperclip size={20} />
                    </button>


                    <textarea
                        value={mensagem}

                        onChange={
                            (event) =>
                                setMensagem(
                                    event.target.value
                                )
                        }

                        onKeyDown={verificarEnter}

                        placeholder={
                            carregando
                                ? "A.R.A. está pensando..."
                                : "Pergunte alguma coisa..."
                        }

                        disabled={carregando}

                        rows={1}
                    />


                    <button
                        type="button"
                        className="ara-composer-action"
                        disabled={carregando}
                        title="Usar voz"
                    >
                        <Mic size={20} />
                    </button>


                    <button
                        type="button"
                        className="ara-send-button"
                        onClick={enviarMensagem}

                        disabled={
                            carregando
                            || !mensagem.trim()
                        }

                        title="Enviar"
                    >
                        <ArrowUp size={21} />
                    </button>

                </div>


                {/*<span className="ara-disclaimer">*/}
                {/*    A.R.A. pode cometer erros. Verifique informações importantes.*/}
                {/*</span>*/}

            </div>

        </main>
    );
}

export default Chat;
