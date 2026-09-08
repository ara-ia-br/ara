import { useState } from "react";
import { LogIn } from "lucide-react";

import api from "../services/api";
import { useAuth } from "../context/AuthContext";


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

            const resposta = await api.post(
                "/auth/login",
                {
                    email,
                    senha
                }
            );

            login(resposta.data);

        } catch (erro) {

            setErro(
                erro.response?.data?.detail
                || "Não foi possível entrar."
            );

        } finally {

            setCarregando(false);
        }
    }


    return (
        <div className="login-page">

            <form
                className="login-card"
                onSubmit={enviar}
            >

                <div className="login-logo">
                    J
                </div>

                <h1>JARVIS</h1>

                <p>
                    Entre para acessar seu assistente pessoal.
                </p>


                <div className="login-field">

                    <label>E-mail</label>

                    <input
                        type="email"
                        value={email}
                        onChange={
                            (event) =>
                                setEmail(event.target.value)
                        }
                        required
                    />

                </div>


                <div className="login-field">

                    <label>Senha</label>

                    <input
                        type="password"
                        value={senha}
                        onChange={
                            (event) =>
                                setSenha(event.target.value)
                        }
                        required
                    />

                </div>


                {erro && (
                    <div className="login-error">
                        {erro}
                    </div>
                )}


                <button
                    className="login-button"
                    disabled={carregando}
                >
                    <LogIn size={18} />

                    {
                        carregando
                            ? "Entrando..."
                            : "Entrar"
                    }
                </button>

            </form>

        </div>
    );
}


export default LoginPage;