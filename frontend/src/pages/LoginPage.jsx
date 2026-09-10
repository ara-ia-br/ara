import { useState } from "react";
import { ArrowRight, LockKeyhole, Mail, ShieldCheck, Sparkles } from "lucide-react";
import api from "../services/api";
import { useAuth } from "../context/AuthContext";
import BrandMark from "../components/BrandMark";

import logoPrincipal from "../assets/brand/logo-principal.png"

function LoginPage() {
    const { login } = useAuth();
    const [email, setEmail] = useState("");
    const [senha, setSenha] = useState("");
    const [erro, setErro] = useState("");
    const [carregando, setCarregando] = useState(false);

    async function enviar(event) {
        event.preventDefault();
        setErro("");
        setCarregando(true);
        try {
            const resposta = await api.post("/auth/login", { email, senha });
            login(resposta.data);
        } catch (error) {
            setErro(error.response?.data?.detail || "Não foi possível entrar.");
        } finally {
            setCarregando(false);
        }
    }

    return (
        <main className="ara-login-page">
            <section className="login-showcase">
                <div className="login-showcase-grid" />
                <BrandMark />
                <div className="login-copy">
                    <span className="page-kicker"><Sparkles size={15} /> AMBIENTE PESSOAL INTELIGENTE</span>
                    <h1>Menos interface.<br />Mais intenção.</h1>
                    <p>A.R.A. reúne conversa, tarefas, contexto e ações em um único ambiente operacional.</p>
                </div>
                <div className="login-signals">
                    <span><i /> CONTEXTO</span>
                    <span><i /> AÇÕES</span>
                    <span><i /> MEMÓRIA</span>
                </div>
            </section>

            <section className="login-access">
                <form className="ara-login-card" onSubmit={enviar}>
                    <div className="login-card-heading">
                        <span className="login-security"><ShieldCheck size={16} /> ACESSO SEGURO</span>
                        <h2>Entre na A.R.A.</h2>
                        <p>Continue de onde parou.</p>
                    </div>

                    <label className="ara-field">
                        <span>E-mail</span>
                        <div><Mail size={17} /><input type="email" value={email} onChange={(event) => setEmail(event.target.value)} autoComplete="email" required /></div>
                    </label>

                    <label className="ara-field">
                        <span>Senha</span>
                        <div><LockKeyhole size={17} /><input type="password" value={senha} onChange={(event) => setSenha(event.target.value)} autoComplete="current-password" required /></div>
                    </label>

                    {erro && <div className="login-error">{erro}</div>}

                    <button className="ara-login-button" disabled={carregando}>
                        <span>{carregando ? "Entrando..." : "Entrar"}</span><ArrowRight size={18} />
                    </button>

                    <small className="login-footnote">Sua sessão utiliza a autenticação já existente no backend.</small>
                </form>
            </section>
        </main>
    );
}

export default LoginPage;
