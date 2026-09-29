from sqlalchemy.orm import Session

from app.models import Mensagem
from app.models.mensagem import RemetenteMensagem
from app.repositories.mensagem_repository import MensagemRepository


class ChatInteractionService:

    # SALVA INTERAÇÃO DO AGENT

    @staticmethod
    def salvar_agent(
            db: Session,
            id_conversa: int,
            conteudo_usuario: str,
            resposta_ara: str
    ) -> None:

        mensagem_usuario = Mensagem(
            id_conversa=id_conversa,
            remetente=RemetenteMensagem.USUARIO,
            conteudo=conteudo_usuario,
            tipo="TEXTO"
        )

        MensagemRepository.criar(
            db, mensagem_usuario
        )

        mensagem_ara = Mensagem(
            id_conversa=id_conversa,
            remetente=RemetenteMensagem.ARA,
            conteudo=resposta_ara,
            tipo="TEXTO",
            modelo_ia="AGENT",
            tempo_processamento=0
        )

        MensagemRepository.criar(
            db,
            mensagem_ara
        )