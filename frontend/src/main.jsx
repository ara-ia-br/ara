import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "@fontsource-variable/inter";
import "@fontsource-variable/inter";
import "./styles/global.css";

import App from "./App.jsx";

import {
    AuthProvider
} from "./context/AuthContext.jsx";

import "./index.css";
import "./styles/index.css";


createRoot(
    document.getElementById("root")
).render(
    <StrictMode>

        <AuthProvider>
            <App />
        </AuthProvider>

    </StrictMode>
);

