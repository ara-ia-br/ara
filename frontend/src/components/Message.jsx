import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

function Message({ autor, children }) {
    const assistente = autor === "ara";

    return (
        <div
            className={
                assistente
                    ? "message ara-message"
                    : "message user-message"
            }
        >
            <div className="message-author">
                {assistente ? (
                    <>
                        <span className="message-signal" />
                        A.R.A.
                    </>
                ) : (
                    "Você"
                )}
            </div>

            <div
                className={
                    assistente
                        ? "message-content markdown-content"
                        : "message-content"
                }
            >
                {assistente ? (
                    <ReactMarkdown
                        remarkPlugins={[remarkGfm]}
                    >
                        {String(children ?? "")}
                    </ReactMarkdown>
                ) : (
                    children
                )}
            </div>
        </div>
    );
}

export default Message;