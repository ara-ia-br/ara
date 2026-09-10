import { ArrowUpRight, Construction, Sparkles } from "lucide-react";

function FeaturePage({ kicker, title, description, icon: Icon, cards = [] }) {
    return (
        <main className="ara-page feature-page">
            <section className="feature-hero">
                <div className="feature-icon">{Icon ? <Icon size={24} /> : <Sparkles size={24} />}</div>
                <div>
                    <span className="page-kicker">{kicker}</span>
                    <h1>{title}</h1>
                    <p>{description}</p>
                </div>
            </section>

            <section className="feature-grid">
                {cards.map((card) => {
                    const CardIcon = card.icon || Construction;
                    return (
                        <article className="feature-card" key={card.title}>
                            <span className="feature-card-icon"><CardIcon size={19} /></span>
                            <div>
                                <h3>{card.title}</h3>
                                <p>{card.text}</p>
                            </div>
                            <ArrowUpRight size={17} />
                        </article>
                    );
                })}
            </section>

            <section className="feature-status panel">
                <span className="status-pulse" />
                <div>
                    <strong>Módulo preparado para integração</strong>
                    <p>A interface já faz parte do novo shell da A.R.A.; as funções que exigem endpoints próprios serão conectadas por fase, sem simular dados inexistentes.</p>
                </div>
            </section>
        </main>
    );
}

export default FeaturePage;
