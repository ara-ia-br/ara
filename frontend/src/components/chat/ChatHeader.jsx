function ChatHeader({ conversaSelecionada }) {
    return (
        <header className="chat-header">
            <div>
                <h2>{conversaSelecionada.titulo}</h2>

                <span className="online">
                    <span className="online-dot" />
                    A.R.A. Online
                </span>
            </div>
        </header>
    );
}

export default ChatHeader;