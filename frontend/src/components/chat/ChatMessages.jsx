import Message from "../Message";

function ChatMessages({ mensagens, carregando, fimMensagensRef }) {
    return (
        <section className="messages">
            {mensagens.length === 0 && (
                <div className="welcome">
                    <div className="jarvis-symbol ara-symbol">A</div>
                    <h2>E aí! O que vamos fazer hoje?</h2>
                    <p>Converse, pergunte ou peça para eu fazer alguma coisa.</p>
                </div>
            )}

            {mensagens.map((item) => (
                <Message key={item.id} autor={item.autor}>
                    {item.conteudo}
                </Message>
            ))}

            {carregando && (
                <div className="message jarvis-message">
                    <div className="message-author">A.R.A.</div>
                    <div className="typing">
                        <span /><span /><span />
                    </div>
                </div>
            )}

            <div ref={fimMensagensRef} />
        </section>
    );
}

export default ChatMessages;
