import { useOutletContext } from "react-router-dom";

import Chat from "../components/Chat";


function ChatPage() {

    const {
        conversaSelecionada,
        setConversaSelecionada,
        conversaCriada
    } = useOutletContext();


    return (
        <Chat
            conversaSelecionada={
                conversaSelecionada
            }
            setConversaSelecionada={
                setConversaSelecionada
            }
            conversaCriada={
                conversaCriada
            }
        />
    );
}


export default ChatPage;