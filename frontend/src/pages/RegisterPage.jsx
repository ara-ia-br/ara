import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { ArrowRight, LockKeyhole, Mail, ShieldCheck, Sparkles, User } from "lucide-react";
import api from "../services/api";
import BrandMark from "../components/BrandMark";

function RegisterPage() {
    const navigate = useNavigate();
    const [nome, setNome] = useState("");
    const [email, setEmail] = useState("");
    const [senha, setSenha] = useState("");
    const [erro, setErro] = useState("");
    const [carregando, setCarregando] = useState(false);
    const [sucesso, setSucesso] = useState(false);

    async function enviar(event) {
        event.preventDefault();
        setErro("");
        setCarregando(true);
        try {
            await api.post("/usuarios", { nome, email, senha });
            setSucesso(true);
            setTimeout(() => navigate("/login"), 1500);
        } catch (error) {
            setErro(error.response?.data?.detail || "Não foi possível criar a conta.");
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
                        <span className="login-security"><ShieldCheck size={16} /> NOVO ACESSO</span>
                        <h2>Crie sua conta</h2>
                        <p>Leva menos de um minuto.</p>
                    </div>

                    <label className="ara-field">
                        <span>Nome</span>
                        <div><User size={17} /><input type="text" value={nome} onChange={(event) => setNome(event.target.value)} autoComplete="name" minLength={2} maxLength={100} required /></div>
                    </label>

                    <label className="ara-field">
                        <span>E-mail</span>
                        <div><Mail size={17} /><input type="email" value={email} onChange={(event) => setEmail(event.target.value)} autoComplete="email" required /></div>
                    </label>

                    <label className="ara-field">
                        <span>Senha</span>
                        <div><LockKeyhole size={17} /><input type="password" value={senha} onChange={(event) => setSenha(event.target.value)} autoComplete="new-password" minLength={8} maxLength={100} required /></div>
                    </label>

                    {erro && <div className="login-error">{erro}</div>}
                    {sucesso && <div className="login-error" style={{ color: "#2ee6a6", borderColor: "#2ee6a6" }}>Conta criada! Redirecionando para o login...</div>}

                    <button className="ara-login-button" disabled={carregando}>
                        <span>{carregando ? "Criando..." : "Criar conta"}</span><ArrowRight size={18} />
                    </button>

                    <small className="login-footnote">
                        Já tem conta? <Link to="/login">Entrar</Link>
                    </small>
                </form>
            </section>
        </main>
    );
}

export default RegisterPage;