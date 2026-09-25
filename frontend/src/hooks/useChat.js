import { useEffect, useRef, useState } from "react";
import api from "../services/api";

// =========================================================
// Toda a lógica de estado e comunicação com o backend
// do chat vive aqui. O componente Chat.jsx só usa o
// que este hook retorna.
// =========================================================

export function useChat(conversaSelecionada, conversaCriada) {
    const [mensagem, setMensagem] = useState("");
    const [mensagens, setMensagens] = useState([]);
    const [carregando, setCarregando] = useState(false);
    const fimMensagensRef = useRef(null);

    async function carregarHistorico() {
        if (!conversaSelecionada) {
            setMensagens([]);
            return;
        }

        try {
            const resposta = await api.get(`/mensagens/conversa/${conversaSelecionada.id_conversa}`);
            const mensagensConvertidas = resposta.data.map((item) => ({
                id: item.id_mensagem,
                autor: item.remetente === "JARVIS" ? "jarvis" : "user",
                conteudo: item.conteudo
            }));
            setMensagens(mensagensConvertidas);
        } catch (erro) {
            console.error("Erro ao carregar histórico:", erro);
        }
    }

    async function enviarMensagem() {
        const texto = mensagem.trim();
        if (!texto || carregando || !conversaSelecionada) return;

        const mensagemUsuario = { id: `temp-${Date.now()}`, autor: "user", conteudo: texto };
        setMensagens((anteriores) => [...anteriores, mensagemUsuario]);
        setMensagem("");
        setCarregando(true);

        try {
            const resposta = await api.post("/chat", {
                id_conversa: conversaSelecionada.id_conversa,
                mensagem: texto
            });

            console.log("===== RESPOSTA /CHAT =====", resposta.data);

            const respostaJarvis = resposta.data?.resposta_jarvis;
            if (!respostaJarvis || typeof respostaJarvis !== "string") {
                console.error("Resposta inválida do backend:", resposta.data);
                throw new Error("O backend não retornou resposta_jarvis.");
            }

            const mensagemJarvis = { id: `jarvis-${Date.now()}`, autor: "jarvis", conteudo: respostaJarvis };
            setMensagens((anteriores) => [...anteriores, mensagemJarvis]);

            // Ferramenta executada (ex: criação de tarefa) — notifica outras
            // partes do app sem derrubar o chat se algo der errado aqui.
            const ferramenta = resposta.data?.ferramenta;
            if (ferramenta && typeof ferramenta === "string" && ferramenta.includes("tarefa")) {
                try {
                    window.dispatchEvent(new CustomEvent("jarvis:tarefas-atualizadas", { detail: { ferramenta } }));
                } catch (erroEvento) {
                    console.error("Erro ao disparar atualização de tarefas:", erroEvento);
                }
            }

            // Atualiza a lista de conversas SOMENTE depois de mostrar
            // a resposta do JARVIS na tela.
            if (typeof conversaCriada === "function") {
                try {
                    await conversaCriada();
                } catch (erroConversa) {
                    console.error("Erro ao atualizar conversas:", erroConversa);
                }
            }
        } catch (erro) {
            console.error("=================================");
            console.error("ERRO AO ENVIAR MENSAGEM");
            console.error("Mensagem:", erro?.message);
            console.error("Código:", erro?.code);
            console.error("Status:", erro?.response?.status);
            console.error("Resposta backend:", erro?.response?.data);
            console.error("Erro completo:", erro);
            console.error("=================================");

            const detalheBackend = erro?.response?.data?.detail;
            const mensagemErro = {
                id: `erro-${Date.now()}`,
                autor: "jarvis",
                conteudo: detalheBackend || "Deu ruim por aqui. Não consegui responder agora."
            };
            setMensagens((anteriores) => [...anteriores, mensagemErro]);
        } finally {
            setCarregando(false);
        }
    }

    function verificarEnter(event) {
        if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault();
            enviarMensagem();
        }
    }

    // Carrega histórico sempre que a conversa selecionada muda
    useEffect(() => {
        carregarHistorico();
    }, [conversaSelecionada?.id_conversa]);

    // Auto scroll para a última mensagem
    useEffect(() => {
        fimMensagensRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [mensagens, carregando]);

    return {
        mensagem,
        setMensagem,
        mensagens,
        carregando,
        enviarMensagem,
        verificarEnter,
        fimMensagensRef
    };
}