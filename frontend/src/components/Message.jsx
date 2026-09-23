function Message({ autor, children }) {
    const assistente = autor === "ara";

    return (
        <div className={assistente ? "message ara-message" : "message user-message"}>
            <div className="message-author">
                {assistente ? <><span className="message-signal" />A.R.A.</> : "VocÃª"}
            </div>
            <div className="message-content">{children}</div>
        </div>
    );
}

export default Message;

