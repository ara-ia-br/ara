import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import {
    BellRing,
    BrainCircuit,
    CalendarDays,
    FileStack,
    FolderKanban,
    Link2,
    Workflow
} from "lucide-react";
import ChatPage from "./pages/ChatPage";
import RegisterPage from "./pages/RegisterPage";
import LoginPage from "./pages/LoginPage";
import TasksPage from "./pages/TasksPage";
import HomePage from "./pages/HomePage";
import FeaturePage from "./pages/FeaturePage";
import AgendaPage from "./pages/AgendaPage";
import SettingsPage from "./pages/SettingsPage";
import ProjectsPage from "./pages/ProjectsPage";
import ConversationsPage from "./pages/ConversationsPage";
import MainLayout from "./layouts/MainLayout";
import { useAuth } from "./context/AuthContext";
import { useOutletContext } from "react-router-dom";

function SettingsRoute() {
    const { cor, setCor, logoChat, setLogoChat, openCommand } = useOutletContext();
    return <SettingsPage cor={cor} setCor={setCor} logoChat={logoChat} setLogoChat={setLogoChat} onOpenCommand={openCommand} />;
}

function App() {
    const { usuario } = useAuth();

    return (
        <BrowserRouter>
            <Routes>
                <Route path="/login" element={usuario ? <Navigate to="/hoje" replace /> : <LoginPage />} />

                <Route path="/cadastro" element={usuario ? <Navigate to="/hoje" replace /> : <RegisterPage />} />

                {usuario && (
                    <Route element={<MainLayout />}>
                        <Route path="/hoje" element={<HomePage />} />
                        <Route path="/chat" element={<ChatPage />} />
                        <Route path="/tarefas" element={<TasksPage />} />
                        <Route path="/agenda" element={<AgendaPage />} />
                        <Route path="/memoria" element={<FeaturePage kicker="CONTEXTO PERSISTENTE" title="Memória" description="Uma área transparente para revisar, editar, reforçar ou esquecer informações usadas pela A.R.A." icon={BrainCircuit} cards={[
                            { title: "Memórias ativas", text: "Preferências, objetivos, projetos e contexto persistente organizados por tipo.", icon: BrainCircuit },
                            { title: "Controle do usuário", text: "Base preparada para editar, fixar, desativar e entender por que algo foi lembrado.", icon: BellRing }
                        ]} />} />
                        <Route path="/arquivos" element={<FeaturePage kicker="CONHECIMENTO" title="Arquivos" description="Documentos e mídia preparados para análise, busca e recuperação contextual." icon={FileStack} cards={[
                            { title: "Biblioteca", text: "Arquivos agrupados por projeto, tipo e atividade recente.", icon: FileStack },
                            { title: "Análise contextual", text: "Base visual para resumo, perguntas e RAG quando os endpoints forem conectados.", icon: BrainCircuit }
                        ]} />} />
                        <Route path="/projetos" element={<ProjectsPage />} />
                        <Route path="/conversas" element={<ConversationsPage />} />
                        <Route path="/arquivadas" element={<Navigate to="/conversas" replace />} />
                        <Route path="/automacoes" element={<FeaturePage kicker="ORQUESTRAÇÃO" title="Automações" description="Rotinas recorrentes e fluxos executáveis com histórico e controle." icon={Workflow} cards={[
                            { title: "Fluxos", text: "Sequências de etapas e ações preparadas para o modelo de automação do backend.", icon: Workflow },
                            { title: "Execuções", text: "Área prevista para acompanhar estado, resultado e falhas de cada execução.", icon: BellRing }
                        ]} />} />
                        <Route path="/integracoes" element={<FeaturePage kicker="CONEXÕES" title="Integrações" description="Serviços externos conectados à A.R.A. com permissões explícitas." icon={Link2} cards={[
                            { title: "Serviços conectados", text: "Hub para provedores, credenciais e permissões de habilidades.", icon: Link2 },
                            { title: "Eventos externos", text: "Preparação para calendários, notificações e fontes de dados externas.", icon: BellRing }
                        ]} />} />
                        <Route path="/configuracoes" element={<SettingsRoute />} />
                    </Route>
                )}

                <Route path="/" element={<Navigate to={usuario ? "/hoje" : "/login"} replace />} />
                <Route path="*" element={<Navigate to={usuario ? "/hoje" : "/login"} replace />} />
            </Routes>
        </BrowserRouter>
    );
}

export default App;
