import { ArrowUp, Mic, Paperclip } from "lucide-react";

function ChatComposer({ mensagem, setMensagem, onEnviar, onEnter, carregando }) {
    return (
        <div className="composer-container">
            <div className="composer">
                <button type="button" className="composer-button" disabled={carregando}>
                    <Paperclip size={20} />
                </button>

                <textarea
                    value={mensagem}
                    onChange={(event) => setMensagem(event.target.value)}
                    onKeyDown={onEnter}
                    placeholder={carregando ? "A.R.A. está pensando..." : "Pergunte alguma coisa..."}
                    disabled={carregando}
                    rows={1}
                />

                <button type="button" className="composer-button" disabled={carregando}>
                    <Mic size={20} />
                </button>

                <button
                    type="button"
                    className="send-button"
                    onClick={onEnviar}
                    disabled={carregando || !mensagem.trim()}
                >
                    <ArrowUp size={21} />
                </button>
            </div>

            <span className="disclaimer">
                A.R.A. pode cometer erros. Verifique informações importantes.
            </span>
        </div>
    );
}

export default ChatComposer;
