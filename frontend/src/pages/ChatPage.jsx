import { useOutletContext } from "react-router-dom";

import Chat from "../components/Chat";


function ChatPage() {

    const {
        conversaSelecionada,
        conversaCriada
    } = useOutletContext();


    return (
        <Chat
            conversaSelecionada={
                conversaSelecionada
            }
            conversaCriada={
                conversaCriada
            }
        />
    );
}


export default ChatPage;