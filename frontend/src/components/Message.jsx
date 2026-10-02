import NativeResultRenderer
    from "./cards/NativeResultRenderer";

import NativeResultRenderer
    from "./cards/NativeResultRenderer";

import araChatLogo
    from "../assets/brand/logo-chat.png";


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
        <div
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
                        : "Você"
                }

            </div>


            <div className="message-content">
                {children}
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

        </div>
    );
}


export default Message;