from sqlalchemy.orm import Session

from app.models.conversa import (
    Conversa,
    StatusConversa
)
from app.repositories.conversa_repository import (
    ConversaRepository
)
from app.repositories.usuario_repository import (
    UsuarioRepository
)
from app.schemas.conversa import ConversaCreate


class ConversaService:

    @staticmethod
    def criar(
        db: Session,
        dados: ConversaCreate
    ) -> Conversa:

        usuario = UsuarioRepository.buscar_por_id(
            db,
            dados.id_usuario
        )

        if usuario is None:
            raise ValueError(
                "Usuário não encontrado."
            )

        conversa = Conversa(
            id_usuario=dados.id_usuario,
            titulo=dados.titulo,
            status=StatusConversa.ATIVA
        )

        return ConversaRepository.criar(
            db,
            conversa
        )

    @staticmethod
    def listar_por_usuario(
        db: Session,
        id_usuario: int
    ) -> list[Conversa]:

        return ConversaRepository.listar_por_usuario(
            db,
            id_usuario
        )

    @staticmethod
    def buscar_por_id(
        db: Session,
        id_conversa: int
    ) -> Conversa:

        conversa = ConversaRepository.buscar_por_id(
            db,
            id_conversa
        )

        if conversa is None:
            raise ValueError(
                "Conversa não encontrada."
            )

        return conversa

    @staticmethod
    def renomear(
        db: Session,
        id_conversa: int,
        novo_titulo: str
    ) -> Conversa:

        conversa = ConversaService.buscar_por_id(
            db,
            id_conversa
        )

        novo_titulo = novo_titulo.strip()

        if not novo_titulo:
            raise ValueError(
                "O título não pode ficar vazio."
            )

        if len(novo_titulo) > 200:
            raise ValueError(
                "O título não pode ter mais de 200 caracteres."
            )

        conversa.titulo = novo_titulo

        return ConversaRepository.salvar(
            db,
            conversa
        )

    @staticmethod
    def arquivar(
        db: Session,
        id_conversa: int
    ) -> Conversa:

        conversa = ConversaService.buscar_por_id(
            db,
            id_conversa
        )

        conversa.status = StatusConversa.ARQUIVADA

        return ConversaRepository.salvar(
            db,
            conversa
        )

    @staticmethod
    def excluir(
        db: Session,
        id_conversa: int
    ) -> None:

        conversa = ConversaService.buscar_por_id(
            db,
            id_conversa
        )

        ConversaRepository.excluir(
            db,
            conversa
        )

    @staticmethod
    def atualizar_atividade(
        db: Session,
        id_conversa: int
    ) -> None:

        conversa = ConversaRepository.buscar_por_id(
            db,
            id_conversa
        )

        if conversa is not None:
            ConversaRepository.atualizar_data(
                db,
                conversa
            )

    @staticmethod
    def gerar_titulo_automatico(
        db: Session,
        id_conversa: int,
        primeira_mensagem: str
    ) -> Conversa:

        conversa = ConversaService.buscar_por_id(
            db,
            id_conversa
        )

        if conversa.titulo != "Nova conversa":
            return conversa

        titulo = primeira_mensagem.strip()

        if len(titulo) > 45:
            titulo = titulo[:45].rstrip() + "..."

        if not titulo:
            titulo = "Nova conversa"

        conversa.titulo = titulo

        return ConversaRepository.salvar(
            db,
            conversa
        )

    @staticmethod
    def listar_arquivadas_por_usuario(
            db: Session,
            id_usuario: int
    ) -> list[Conversa]:

        return ConversaRepository.listar_arquivadas_por_usuario(
            db,
            id_usuario
        )

    @staticmethod
    def restaurar(
            db: Session,
            id_conversa: int
    ) -> Conversa:

        conversa = ConversaService.buscar_por_id(
            db,
            id_conversa
        )

        conversa.status = StatusConversa.ATIVA

        return ConversaRepository.salvar(
            db,
            conversa
        )