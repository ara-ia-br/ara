from sqlalchemy.orm import Session

from app.models.mensagem import Mensagem
from app.repositories.conversa_repository import ConversaRepository
from app.repositories.mensagem_repository import MensagemRepository
from app.schemas.mensagem import MensagemCreate


class MensagemService:

    @staticmethod
    def criar(
        db: Session,
        dados: MensagemCreate
    ) -> Mensagem:

        conversa = (
            ConversaRepository.buscar_por_id(
                db,
                dados.id_conversa
            )
        )

        if conversa is None:
            raise ValueError(
                "Conversa não encontrada."
            )

        mensagem = Mensagem(
            id_conversa=dados.id_conversa,
            remetente=dados.remetente,
            conteudo=dados.conteudo,
            tipo=dados.tipo
        )

        return MensagemRepository.criar(
            db,
            mensagem
        )

    @staticmethod
    def listar_por_conversa(
        db: Session,
        id_conversa: int
    ) -> list[Mensagem]:

        return (
            MensagemRepository.listar_por_conversa(
                db,
                id_conversa
            )
        )