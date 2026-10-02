import { ArrowUpRight, Construction, Sparkles } from "lucide-react";

function FeaturePage({ kicker, title, description, icon: Icon, cards = [] }) {
    return (
        <main className="ara-page feature-page">
            <header className="feature-hero">
                <div className="feature-hero-icon">
                    {Icon ? <Icon size={28} /> : <Sparkles size={28} />}
                </div>

                <div className="feature-hero-copy">
                    <span className="page-kicker">{kicker}</span>
                    <h1>{title}</h1>
                    <p>{description}</p>
                </div>
            </header>

            <section className="feature-overview">
                <div className="feature-overview-copy">
                    <span className="feature-label">CENTRO DE CONTROLE</span>
                    <h2>Seu espaço de {title.toLowerCase()}</h2>
                    <p>
                        Tudo fica organizado em uma interface única, com mais espaço,
                        contraste e informações fáceis de encontrar.
                    </p>
                </div>

                <div className="feature-overview-status">
                    <span className="status-pulse" />
                    <div>
                        <strong>Estrutura pronta</strong>
                        <small>Interface conectável ao backend</small>
                    </div>
                </div>
            </section>

            <section className="feature-grid">
                {cards.map((card) => {
                    const CardIcon = card.icon || Construction;

                    return (
                        <article className="feature-card" key={card.title}>
                            <div className="feature-card-top">
                                <span className="feature-card-icon">
                                    <CardIcon size={21} />
                                </span>
                                <ArrowUpRight size={18} className="feature-card-arrow" />
                            </div>

                            <div className="feature-card-copy">
                                <h3>{card.title}</h3>
                                <p>{card.text}</p>
                            </div>
                        </article>
                    );
                })}
            </section>

            <section className="feature-status panel">
                <div className="feature-status-icon">
                    <Sparkles size={18} />
                </div>
                <div>
                    <strong>Base da A.R.A. preparada para crescer</strong>
                    <p>
                        Esta área mantém a mesma linguagem visual das outras telas e pode
                        receber suas funções reais sem precisar refazer a estrutura da interface.
                    </p>
                </div>
            </section>
        </main>
    );
}

export default FeaturePage;
