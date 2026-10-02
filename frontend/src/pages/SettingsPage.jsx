import { MonitorCog, Keyboard, ShieldCheck, Check } from "lucide-react";

const cores = [
    { id: "mint", nome: "Verde água", hex: "#00dba6" },
    { id: "forest", nome: "Verde escuro", hex: "#087565" },
    { id: "red", nome: "Vermelho", hex: "#a51f2b" },
    { id: "gray", nome: "Cinza", hex: "#65635d" },
    { id: "cyan", nome: "Ciano", hex: "#00b9e8" },
    { id: "lime", nome: "Verde-limão", hex: "#24e78b" },
];

function SettingsPage({ cor, setCor, logoChat, setLogoChat, onOpenCommand }) {
    return (
        <main className="ara-page settings-page">
            <section className="page-heading-block">
                <span className="page-kicker">CONTROLE DO SISTEMA</span>
                <h1>Personalização</h1>
                <p>Escolha a cor de destaque e a aparência da A.R.A. durante as conversas.</p>
            </section>

            <section className="settings-grid">
                <article className="setting-card settings-wide">
                    <div><MonitorCog size={20} /><span><strong>Cor de destaque</strong><small>O tema escuro é o padrão. Altere apenas a cor dos detalhes da interface.</small></span></div>
                    <div className="accent-options" role="group" aria-label="Escolha uma cor">
                        {cores.map((item) => (
                            <button key={item.id} type="button" className={`accent-option ${cor === item.id ? "active" : ""}`}
                                onClick={() => setCor(item.id)} aria-label={item.nome} title={item.nome}>
                                <span style={{ backgroundColor: item.hex }} />
                                <small>{item.nome}</small>
                                {cor === item.id && <Check size={13} />}
                            </button>
                        ))}
                    </div>
                </article>

                <article className="setting-card settings-wide">
                    <div><MonitorCog size={20} /><span><strong>Logo da conversa</strong><small>Escolha a imagem que representa a A.R.A. nas mensagens.</small></span></div>
                    <div className="chat-logo-options" role="group" aria-label="Escolha o logo da conversa">
                        {["1", "2", "3"].map((item) => (
                            <button key={item} type="button" className={`chat-logo-option ${logoChat === item ? "active" : ""}`}
                                onClick={() => setLogoChat(item)} aria-pressed={logoChat === item}>
                                <span className={`logo-placeholder logo-placeholder-${item}`}>Logo {item}</span>
                                <small>Logo {item}</small>
                            </button>
                        ))}
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
