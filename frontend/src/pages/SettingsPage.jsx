import { Moon, Sun, MonitorCog, Keyboard, ShieldCheck } from "lucide-react";

function SettingsPage({ tema, setTema, onOpenCommand }) {
    return (
        <main className="ara-page settings-page">
            <section className="page-heading-block">
                <span className="page-kicker">CONTROLE DO SISTEMA</span>
                <h1>Configurações</h1>
                <p>Personalize a experiência da A.R.A. sem alterar o comportamento do backend.</p>
            </section>

            <section className="settings-grid">
                <article className="setting-card">
                    <div><MonitorCog size={20} /><span><strong>Aparência</strong><small>Tema visual do workspace</small></span></div>
                    <div className="theme-switcher">
                        <button className={tema === "dark" ? "active" : ""} onClick={() => setTema("dark")}><Moon size={16} /> Escuro</button>
                        <button className={tema === "light" ? "active" : ""} onClick={() => setTema("light")}><Sun size={16} /> Claro</button>
                    </div>
                </article>

                <article className="setting-card">
                    <div><Keyboard size={20} /><span><strong>Command Center</strong><small>Navegação instantânea</small></span></div>
                    <button className="setting-action" onClick={onOpenCommand}>Abrir agora <kbd>Ctrl K</kbd></button>
                </article>

                <article className="setting-card">
                    <div><ShieldCheck size={20} /><span><strong>Privacidade</strong><small>Memória, integrações e dados</small></span></div>
                    <span className="setting-note">Controles detalhados entram junto dos respectivos módulos.</span>
                </article>
            </section>
        </main>
    );
}

export default SettingsPage;
