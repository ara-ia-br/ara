function Message({
    autor,
    children
}) {

    const jarvis = autor === "jarvis";

    return (
        <div
            className={
                jarvis
                    ? "message jarvis-message"
                    : "message user-message"
            }
        >

            <div className="message-author">
                {jarvis ? "JARVIS" : "Você"}
            </div>

            <div className="message-content">
                {children}
            </div>

        </div>
    );
}

export default Message;