import {
    BrowserRouter,
    Navigate,
    Route,
    Routes
} from "react-router-dom";

import ChatPage from "./pages/ChatPage";
import LoginPage from "./pages/LoginPage";
import TasksPage from "./pages/TasksPage";

import MainLayout from "./layouts/MainLayout";

import { useAuth } from "./context/AuthContext";


function App() {

    const { usuario } = useAuth();


    return (
        <BrowserRouter>

            <Routes>

                {/* LOGIN */}

                <Route
                    path="/login"
                    element={
                        usuario
                            ? (
                                <Navigate
                                    to="/chat"
                                    replace
                                />
                            )
                            : (
                                <LoginPage />
                            )
                    }
                />


                {/* ÁREA AUTENTICADA */}

                {
                    usuario
                        ? (

                            <Route
                                element={<MainLayout />}
                            >

                                <Route
                                    path="/chat"
                                    element={<ChatPage />}
                                />

                                <Route
                                    path="/tarefas"
                                    element={<TasksPage />}
                                />

                            </Route>

                        )
                        : null
                }


                {/* ROTA INICIAL */}

                <Route
                    path="/"
                    element={
                        <Navigate
                            to={
                                usuario
                                    ? "/chat"
                                    : "/login"
                            }
                            replace
                        />
                    }
                />


                {/* QUALQUER ROTA DESCONHECIDA */}

                <Route
                    path="*"
                    element={
                        <Navigate
                            to={
                                usuario
                                    ? "/chat"
                                    : "/login"
                            }
                            replace
                        />
                    }
                />

            </Routes>

        </BrowserRouter>
    );
}


export default App;