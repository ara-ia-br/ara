import { useState } from "react";
import {
    ArrowRight,
    Eye,
    EyeOff,
    LockKeyhole,
    Mail,
    ShieldCheck,
    Sparkles,
    User
} from "lucide-react";

import api from "../services/api";
import BrandMark from "../components/BrandMark";
import { Link, useNavigate } from "react-router-dom";


function RegisterPage() {
    const navigate = useNavigate();

    const [nome, setNome] = useState("");
    const [email, setEmail] = useState("");
    const [senha, setSenha] = useState("");

    const [mostrarSenha, setMostrarSenha] = useState(false);

    const [erro, setErro] = useState("");
    const [sucesso, setSucesso] = useState("");
    const [carregando, setCarregando] = useState(false);


    async function enviar(event) {
        event.preventDefault();

        setErro("");
        setSucesso("");
        setCarregando(true);

        try {

            await api.post(
                "/usuarios",
                {
                    nome,
                    email,
                    senha
                }
            );

            setSucesso(
                "Conta criada com sucesso! Redirecionando..."
            );

            setTimeout(() => {
                navigate("/login");
            }, 1500);

        } catch (error) {

            setErro(
                error.response?.data?.detail ||
                "Não foi possível criar sua conta."
            );

        } finally {
            setCarregando(false);
        }
    }


    return (
        <main className="ara-login-page">

            {/* LADO ESQUERDO */}
            <section className="login-showcase">

                <div className="login-showcase-grid" />

                <BrandMark />

                <div className="login-copy">

                    <span className="page-kicker">
                        <Sparkles size={15} />
                        AMBIENTE PESSOAL INTELIGENTE
                    </span>

                    <h1>
                        Menos interface.
                        <br />
                        Mais intenção.
                    </h1>

                    <p>
                        A.R.A. reúne conversa, tarefas,
                        contexto e ações em um único
                        ambiente operacional.
                    </p>

                </div>


                <div className="login-signals">

                    <span>
                        <i />
                        CONTEXTO
                    </span>

                    <span>
                        <i />
                        AÇÕES
                    </span>

                    <span>
                        <i />
                        MEMÓRIA
                    </span>

                </div>

            </section>


            {/* LADO DIREITO */}
            <section className="login-access">

                <form
                    className="ara-login-card"
                    onSubmit={enviar}
                >

                    <div className="login-card-heading">

                        <span className="login-security">
                            <ShieldCheck size={16} />
                            NOVO ACESSO
                        </span>

                        <h2>
                            Crie sua conta
                        </h2>

                        <p>
                            Comece a usar a A.R.A.
                        </p>

                    </div>


                    {/* NOME */}
                    <label className="ara-field">

                        <span>
                            Nome
                        </span>

                        <div>

                            <User size={17} />

                            <input
                                type="text"
                                value={nome}
                                onChange={(event) =>
                                    setNome(event.target.value)
                                }
                                autoComplete="name"
                                required
                            />

                        </div>

                    </label>


                    {/* E-MAIL */}
                    <label className="ara-field">

                        <span>
                            E-mail
                        </span>

                        <div>

                            <Mail size={17} />

                            <input
                                type="email"
                                value={email}
                                onChange={(event) =>
                                    setEmail(event.target.value)
                                }
                                autoComplete="email"
                                required
                            />

                        </div>

                    </label>


                    {/* SENHA */}
                    <label className="ara-field">

                        <span>
                            Senha
                        </span>

                        <div className="password-field">

                            <LockKeyhole size={17} />

                            <input
                                type={
                                    mostrarSenha
                                        ? "text"
                                        : "password"
                                }
                                value={senha}
                                onChange={(event) =>
                                    setSenha(event.target.value)
                                }
                                autoComplete="new-password"
                                required
                            />

                            <button
                                type="button"
                                className="password-toggle"
                                onClick={() =>
                                    setMostrarSenha(
                                        (valor) => !valor
                                    )
                                }
                                aria-label={
                                    mostrarSenha
                                        ? "Ocultar senha"
                                        : "Mostrar senha"
                                }
                                title={
                                    mostrarSenha
                                        ? "Ocultar senha"
                                        : "Mostrar senha"
                                }
                            >
                                {mostrarSenha ? (
                                    <EyeOff size={18} />
                                ) : (
                                    <Eye size={18} />
                                )}
                            </button>

                        </div>

                    </label>


                    {/* ERRO */}
                    {erro && (
                        <div className="login-error">
                            {erro}
                        </div>
                    )}


                    {/* SUCESSO */}
                    {sucesso && (
                        <div className="login-success">
                            {sucesso}
                        </div>
                    )}


                    {/* CRIAR CONTA */}
                    <button
                        type="submit"
                        className="ara-login-button"
                        disabled={carregando}
                    >

                        <span>
                            {carregando
                                ? "Criando..."
                                : "Criar conta"}
                        </span>

                        <ArrowRight size={18} />

                    </button>


                    <small className="login-footnote">

                        Já tem conta?{" "}

                        <Link to="/login">
                            Entrar
                        </Link>

                    </small>

                </form>

            </section>

        </main>
    );
}


export default RegisterPage;