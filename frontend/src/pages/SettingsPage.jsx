import {
    useEffect,
    useState
} from "react";

import {
    BrainCircuit,
    Check,
    Keyboard,
    LoaderCircle,
    MonitorCog,
    Moon,
    Save,
    ShieldCheck,
    Smile,
    Sparkles,
    Sun
} from "lucide-react";

import api from "../services/api";

import "../settings-personalization.css";


/* =========================================================
   CONVERSÃO ENUM -> SLIDER
========================================================= */

function enumParaSlider(
    tipo,
    valor
) {
    const mapas = {
        tom: {
            INFORMAL: 0,
            ADAPTATIVO: 50,
            FORMAL: 100
        },

        formalidade: {
            BAIXA: 0,
            MEDIA: 50,
            ADAPTATIVA: 50,
            ALTA: 100
        },

        nivel_detalhe: {
            BAIXO: 0,
            MEDIO: 50,
            ALTO: 100
        },

        estilo_resposta: {
            DIRETO: 0,
            NATURAL: 100
        }
    };

    return mapas?.[tipo]?.[valor] ?? 50;
}

/* =========================================================
   LABEL DO ENUM
========================================================= */

function formatarValor(
    tipo,
    valor
) {

    const labels = {

        tom: {
            INFORMAL: "Informal",
            ADAPTATIVO: "Adaptativo",
            FORMAL: "Formal"
        },

        formalidade: {
            BAIXA: "Baixa",
            MEDIA: "Média",
            ADAPTATIVA: "Adaptativa",
            ALTA: "Alta"
        },

        nivel_detalhe: {
            BAIXO: "Baixo",
            MEDIO: "Médio",
            ALTO: "Alto"
        },

        estilo_resposta: {
            DIRETO: "Direto",
            NATURAL: "Natural"
        }
    };


   return labels?.[tipo]?.[valor] ?? valor;
}


function sliderParaEnum(
    tipo,
    valor
) {

    const numero = Number(valor);


    if (tipo === "tom") {

        if (numero < 34) {
            return "INFORMAL";
        }

        if (numero < 67) {
            return "ADAPTATIVO";
        }

        return "FORMAL";
    }


    if (tipo === "formalidade") {

        if (numero < 34) {
            return "BAIXA";
        }

        if (numero < 67) {
            return "MEDIA";
        }

        return "ALTA";
    }


    if (tipo === "nivel_detalhe") {

        if (numero < 34) {
            return "BAIXO";
        }

        if (numero < 67) {
            return "MEDIO";
        }

        return "ALTO";
    }


    if (tipo === "estilo_resposta") {

        return numero < 50
            ? "DIRETO"
            : "NATURAL";
    }


    return null;
}


/* =========================================================
   COMPONENTE DE SLIDER
========================================================= */

function PersonalizationSlider({
    titulo,
    descricao,
    esquerda,
    direita,
    tipo,
    valor,
    onChange
}) {

    return (

        <div className="personalization-slider">

            <div className="slider-heading">

                <div>

                    <strong>
                        {titulo}
                    </strong>

                    <small>
                        {descricao}
                    </small>

                </div>


                <span className="slider-current-value">

                    {
                        formatarValor(
                            tipo,
                            valor
                        )
                    }

                </span>

            </div>


            <div className="slider-labels">

                <span>
                    {esquerda}
                </span>

                <span>
                    {direita}
                </span>

            </div>


            <input
                type="range"

                min="0"
                max="100"
                step="1"

                value={
                    enumParaSlider(
                        tipo,
                        valor
                    )
                }

                onChange={
                    (event) =>
                        onChange(
                            sliderParaEnum(
                                tipo,
                                event.target.value
                            )
                        )
                }

                aria-label={titulo}
            />

        </div>
    );
}


/* =========================================================
   SETTINGS PAGE
========================================================= */

function SettingsPage({
    tema,
    setTema,
    onOpenCommand
}) {

    /* =====================================================
       ESTADO
    ===================================================== */

    const [perfil, setPerfil] = useState({

        tom:
            "ADAPTATIVO",

        formalidade:
            "ADAPTATIVA",

        nivel_detalhe:
            "MEDIO",

        usar_emojis:
            true,

        estilo_resposta:
            "NATURAL",

        instrucoes_personais:
            ""
    });


    const [carregando, setCarregando] =
        useState(true);


    const [salvando, setSalvando] =
        useState(false);


    const [mensagemStatus, setMensagemStatus] =
        useState("");


    const [erro, setErro] =
        useState("");


    /* =====================================================
       CARREGAR PERSONALIZAÇÃO
    ===================================================== */

    useEffect(
        () => {

            async function carregarPerfil() {

                setCarregando(true);

                setErro("");

                setMensagemStatus("");


                try {

                    const resposta = await api.get(
                        "/perfil-personalizacao/me"
                    );


                    setPerfil({

                        tom:
                            resposta.data.tom
                            ?? "ADAPTATIVO",

                        formalidade:
                            resposta.data.formalidade
                            ?? "ADAPTATIVA",

                        nivel_detalhe:
                            resposta.data.nivel_detalhe
                            ?? "MEDIO",

                        usar_emojis:
                            resposta.data.usar_emojis
                            ?? true,

                        estilo_resposta:
                            resposta.data.estilo_resposta
                            ?? "NATURAL",

                        instrucoes_personais:
                            resposta
                                .data
                                .instrucoes_personais
                            ?? ""
                    });


                } catch (erroRequisicao) {

                    console.error(
                        "Erro ao carregar personalização:",
                        erroRequisicao
                    );


                    setErro(
                        erroRequisicao
                            ?.response
                            ?.data
                            ?.detail
                        || (
                            "Não foi possível carregar "
                            + "suas preferências."
                        )
                    );


                } finally {

                    setCarregando(false);
                }
            }


            carregarPerfil();

        },
        []
    );


    /* =====================================================
       ALTERAR CAMPO
    ===================================================== */

    function alterarCampo(
        campo,
        valor
    ) {

        setPerfil(
            (anterior) => ({

                ...anterior,

                [campo]:
                    valor
            })
        );


        setMensagemStatus("");

        setErro("");
    }


    /* =====================================================
       SALVAR
    ===================================================== */

    async function salvarPersonalizacao() {

        if (salvando) {
            return;
        }


        setSalvando(true);

        setErro("");

        setMensagemStatus("");


        try {

            const resposta = await api.patch(
                "/perfil-personalizacao/me",
                {

                    tom:
                        perfil.tom,

                    formalidade:
                        perfil.formalidade,

                    nivel_detalhe:
                        perfil.nivel_detalhe,

                    usar_emojis:
                        perfil.usar_emojis,

                    estilo_resposta:
                        perfil.estilo_resposta,

                    instrucoes_personais:
                        perfil
                            .instrucoes_personais
                            .trim()
                        || null
                }
            );


            setPerfil({

                tom:
                    resposta.data.tom,

                formalidade:
                    resposta.data.formalidade,

                nivel_detalhe:
                    resposta.data.nivel_detalhe,

                usar_emojis:
                    resposta.data.usar_emojis,

                estilo_resposta:
                    resposta.data.estilo_resposta,

                instrucoes_personais:
                    resposta
                        .data
                        .instrucoes_personais
                    ?? ""
            });


            setMensagemStatus(
                "Preferências salvas."
            );


        } catch (erroRequisicao) {

            console.error(
                "Erro ao salvar personalização:",
                erroRequisicao
            );


            setErro(
                erroRequisicao
                    ?.response
                    ?.data
                    ?.detail
                || (
                    "Não foi possível salvar "
                    + "suas preferências."
                )
            );


        } finally {

            setSalvando(false);
        }
    }


    /* =====================================================
       RENDER
    ===================================================== */

    return (

        <main className="ara-page settings-page">

            {/* =============================================
                CABEÇALHO
            ============================================= */}

            <section className="page-heading-block">

                <span className="page-kicker">
                    CONTROLE DO SISTEMA
                </span>


                <h1>
                    Configurações
                </h1>


                <p>
                    Personalize como a A.R.A. conversa
                    com você e como o workspace
                    se comporta.
                </p>

            </section>


            {/* =============================================
                PERSONALIZAÇÃO
            ============================================= */}

            <section className="personalization-section">

                <div className="settings-section-heading">

                    <div className="settings-section-icon">

                        <BrainCircuit size={19} />

                    </div>


                    <div>

                        <span className="settings-section-kicker">
                            PERSONALIZAÇÃO
                        </span>


                        <h2>
                            Ajuste o jeito da A.R.A.
                        </h2>


                        <p>
                            Arraste os controles para definir
                            como você prefere conversar com a A.R.A.
                            Pedidos específicos durante uma conversa
                            continuam tendo prioridade.
                        </p>

                    </div>

                </div>


                {
                    carregando
                    ? (

                        <div className="personalization-loading">

                            <LoaderCircle
                                size={20}
                                className="settings-spinner"
                            />

                            <span>
                                Carregando preferências...
                            </span>

                        </div>

                    )
                    : (

                        <div className="personalization-panel">

                            {/* TOM */}

                            <PersonalizationSlider

                                titulo="Tom"

                                descricao={
                                    "De uma conversa mais casual "
                                    + "até uma comunicação mais formal."
                                }

                                esquerda="Informal"

                                direita="Formal"

                                tipo="tom"

                                valor={
                                    perfil.tom
                                }

                                onChange={
                                    (valor) =>
                                        alterarCampo(
                                            "tom",
                                            valor
                                        )
                                }
                            />


                            {/* FORMALIDADE */}

                            <PersonalizationSlider

                                titulo="Formalidade"

                                descricao={
                                    "Ajuste o nível de formalidade "
                                    + "das respostas."
                                }

                                esquerda="Baixa"

                                direita="Alta"

                                tipo="formalidade"

                                valor={
                                    perfil.formalidade
                                }

                                onChange={
                                    (valor) =>
                                        alterarCampo(
                                            "formalidade",
                                            valor
                                        )
                                }
                            />


                            {/* DETALHE */}

                            <PersonalizationSlider

                                titulo="Nível de detalhe"

                                descricao={
                                    "Escolha entre respostas "
                                    + "mais curtas ou completas."
                                }

                                esquerda="Curto"

                                direita="Detalhado"

                                tipo="nivel_detalhe"

                                valor={
                                    perfil.nivel_detalhe
                                }

                                onChange={
                                    (valor) =>
                                        alterarCampo(
                                            "nivel_detalhe",
                                            valor
                                        )
                                }
                            />


                            {/* ESTILO */}

                            <PersonalizationSlider

                                titulo="Estilo da resposta"

                                descricao={
                                    "Controle o equilíbrio entre "
                                    + "objetividade e conversa natural."
                                }

                                esquerda="Direto"

                                direita="Natural"

                                tipo="estilo_resposta"

                                valor={
                                    perfil.estilo_resposta
                                }

                                onChange={
                                    (valor) =>
                                        alterarCampo(
                                            "estilo_resposta",
                                            valor
                                        )
                                }
                            />


                            {/* EMOJIS */}

                            <div className="personalization-toggle-card">

                                <div>

                                    <Smile size={18} />


                                    <span>

                                        <strong>
                                            Emojis
                                        </strong>


                                        <small>
                                            Permitir emojis quando
                                            fizer sentido na conversa.
                                        </small>

                                    </span>

                                </div>


                                <button
                                    type="button"

                                    className={
                                        perfil.usar_emojis
                                            ? "ara-switch active"
                                            : "ara-switch"
                                    }

                                    onClick={
                                        () =>
                                            alterarCampo(
                                                "usar_emojis",
                                                !perfil.usar_emojis
                                            )
                                    }

                                    aria-label={
                                        "Alternar uso de emojis"
                                    }
                                >

                                    <span />

                                </button>

                            </div>


                            {/* INSTRUÇÕES */}

                            <label className="personalization-instructions">

                                <div>

                                    <Sparkles size={18} />


                                    <span>

                                        <strong>
                                            Instruções pessoais
                                        </strong>


                                        <small>
                                            Dê orientações adicionais
                                            sobre como prefere receber
                                            as respostas.
                                        </small>

                                    </span>

                                </div>


                                <textarea

                                    value={
                                        perfil
                                            .instrucoes_personais
                                    }

                                    onChange={
                                        (event) =>
                                            alterarCampo(
                                                "instrucoes_personais",
                                                event.target.value
                                            )
                                    }

                                    placeholder={
                                        "Ex.: prefiro exemplos em Java, "
                                        + "respostas objetivas, linguagem "
                                        + "simples e exemplos práticos."
                                    }

                                    maxLength={2000}

                                    rows={4}
                                />


                                <span className="personalization-counter">

                                    {
                                        perfil
                                            .instrucoes_personais
                                            .length
                                    }

                                    /2000

                                </span>

                            </label>


                            {/* FOOTER */}

                            <div className="personalization-footer">

                                <div className="personalization-feedback">

                                    {
                                        mensagemStatus
                                        && (

                                            <span className="settings-success">

                                                <Check size={15} />

                                                {mensagemStatus}

                                            </span>

                                        )
                                    }


                                    {
                                        erro
                                        && (

                                            <span className="settings-error">

                                                {erro}

                                            </span>

                                        )
                                    }

                                </div>


                                <button
                                    type="button"

                                    className="personalization-save"

                                    onClick={
                                        salvarPersonalizacao
                                    }

                                    disabled={
                                        salvando
                                    }
                                >

                                    {
                                        salvando
                                        ? (

                                            <LoaderCircle
                                                size={16}
                                                className="settings-spinner"
                                            />

                                        )
                                        : (

                                            <Save size={16} />

                                        )
                                    }


                                    <span>

                                        {
                                            salvando
                                                ? "Salvando..."
                                                : "Salvar alterações"
                                        }

                                    </span>

                                </button>

                            </div>

                        </div>

                    )
                }

            </section>


            {/* =============================================
                WORKSPACE
            ============================================= */}

            <section className="settings-secondary">

                <div className="settings-section-heading compact">

                    <div>

                        <span className="settings-section-kicker">
                            WORKSPACE
                        </span>


                        <h2>
                            Sistema
                        </h2>

                    </div>

                </div>


                <div className="settings-grid">

                    {/* APARÊNCIA */}

                    <article className="setting-card">

                        <div>

                            <MonitorCog size={20} />


                            <span>

                                <strong>
                                    Aparência
                                </strong>


                                <small>
                                    Tema visual do workspace
                                </small>

                            </span>

                        </div>


                        <div className="theme-switcher">

                            <button

                                className={
                                    tema === "dark"
                                        ? "active"
                                        : ""
                                }

                                onClick={
                                    () =>
                                        setTema("dark")
                                }
                            >

                                <Moon size={16} />

                                Escuro

                            </button>


                            <button

                                className={
                                    tema === "light"
                                        ? "active"
                                        : ""
                                }

                                onClick={
                                    () =>
                                        setTema("light")
                                }
                            >

                                <Sun size={16} />

                                Claro

                            </button>

                        </div>

                    </article>


                    {/* COMMAND CENTER */}

                    <article className="setting-card">

                        <div>

                            <Keyboard size={20} />


                            <span>

                                <strong>
                                    Command Center
                                </strong>


                                <small>
                                    Navegação instantânea
                                </small>

                            </span>

                        </div>


                        <button
                            type="button"
                            className="setting-action"
                            onClick={onOpenCommand}
                        >

                            Abrir agora

                            <kbd>
                                Ctrl K
                            </kbd>

                        </button>

                    </article>


                    {/* PRIVACIDADE */}

                    <article className="setting-card">

                        <div>

                            <ShieldCheck size={20} />


                            <span>

                                <strong>
                                    Privacidade
                                </strong>


                                <small>
                                    Memória, integrações e dados
                                </small>

                            </span>

                        </div>


                        <span className="setting-note">

                            Controles detalhados entram
                            junto dos respectivos módulos.

                        </span>

                    </article>

                </div>

            </section>

        </main>
    );
}


export default SettingsPage;