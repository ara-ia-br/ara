import NativeResultRenderer
    from "./cards/NativeResultRenderer";

import araChatLogo
    from "../assets/brand/logo-chat.png";


import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";


function Message({
    autor,
    children,
    visualizacao = null
}) {

    const assistente = (
        autor === "jarvis"
        || autor === "ara"
    );


    return (
        <article
            className={
                assistente
                    ? "message jarvis-message ara-message"
                    : "message user-message"
            }
        >

            <div className="message-author">

                {
                    assistente
                        ? (
                            <>
                                <span className="message-avatar ara-avatar">
                                    <img
                                        src={araChatLogo}
                                        alt=""
                                        aria-hidden="true"
                                    />
                                </span>

                                <span>
                                    A.R.A.
                                </span>
                            </>
                        )
                        : (
                            <span>
                                Você
                            </span>
                        )
                }

            </div>


            <div className="message-content">
    {
        assistente
            ? (
                <ReactMarkdown
                    remarkPlugins={[
                        remarkGfm
                    ]}
                >
                    {
                        typeof children === "string"
                            ? children
                            : ""
                    }
                </ReactMarkdown>
            )
            : (
                children
            )
    }
</div>


            {
                assistente
                && visualizacao
                && (
                    <NativeResultRenderer
                        visualizacao={
                            visualizacao
                        }
                    />
                )
            }

        </article>
    );
}


export default Message;
