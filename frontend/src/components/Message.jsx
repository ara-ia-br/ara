import NativeResultRenderer
    from "./cards/NativeResultRenderer";


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
                                <span className="message-signal" />
                                A.R.A.
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