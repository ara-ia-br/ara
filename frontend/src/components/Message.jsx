function Message({ autor, children }) {
    const assistente = autor === "jarvis" || autor === "ara";
    const logo = typeof window !== "undefined" ? (localStorage.getItem("ara.chatLogo") || "1") : "1";

    return (
        <article className={assistente ? "message jarvis-message ara-message" : "message user-message"}>
            <div className="message-author">
                {assistente ? (
                    <>
                        <span className={`message-avatar ara-avatar logo-placeholder logo-placeholder-${logo}`}>Logo {logo}</span>
                        <span>A.R.A.</span>
                    </>
                ) : <span>Você</span>}
            </div>
            <div className="message-content">{children}</div>
        </article>
    );
}
export default Message;
