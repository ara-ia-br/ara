import {
    createContext,
    useContext,
    useState
} from "react";


const AuthContext = createContext(null);


export function AuthProvider({ children }) {

    const [usuario, setUsuario] = useState(() => {

        const salvo = localStorage.getItem(
            "ara_usuario"
        );

        return salvo
            ? JSON.parse(salvo)
            : null;
    });


    function login(dados) {

        const usuarioLogado = {
            id_usuario: dados.id_usuario,
            nome: dados.nome,
            email: dados.email,
            access_token: dados.access_token
        };

        localStorage.setItem(
            "ara_usuario",
            JSON.stringify(usuarioLogado)
        );

        setUsuario(usuarioLogado);
    }


    function logout() {

        localStorage.removeItem(
            "ara_usuario"
        );

        setUsuario(null);
    }


    return (
        <AuthContext.Provider
            value={{
                usuario,
                login,
                logout
            }}
        >
            {children}
        </AuthContext.Provider>
    );
}


export function useAuth() {
    return useContext(AuthContext);
}