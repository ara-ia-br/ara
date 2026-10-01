import axios from "axios";


const api = axios.create({

    baseURL:
        import.meta.env.VITE_API_URL
        || "",

    timeout:
        120000
});


/* =========================================================
   ADICIONAR JWT AUTOMATICAMENTE
========================================================= */

api.interceptors.request.use(

    (config) => {

        try {

            const salvo = localStorage.getItem(
                "ara_usuario"
            );


            if (!salvo) {
                return config;
            }


            const usuario = JSON.parse(
                salvo
            );


            const token = (
                usuario
                    ?.access_token
            );


            if (token) {

                config.headers.Authorization =
                    `Bearer ${token}`;
            }


        } catch (erro) {

            console.error(
                "Erro ao preparar autenticação da API:",
                erro
            );
        }


        return config;
    },


    (erro) => {

        return Promise.reject(
            erro
        );
    }
);


export default api;