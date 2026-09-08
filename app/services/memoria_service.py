from sqlalchemy.orm import Session

from app.models.memoria import Memoria
from app.repositories.memoria_repository import MemoriaRepository
from app.repositories.usuario_repository import UsuarioRepository
from app.schemas.memoria import MemoriaCreate


class MemoriaService:

    @staticmethod
    def criar(
        db: Session,
        dados: MemoriaCreate
    ) -> Memoria:

        usuario = UsuarioRepository.buscar_por_id(
            db,
            dados.id_usuario
        )

        if usuario is None:
            raise ValueError(
                "Usuário não encontrado."
            )

        memoria = Memoria(
            id_usuario=dados.id_usuario,
            tipo_memoria=dados.tipo_memoria,
            conteudo=dados.conteudo,
            importancia=dados.importancia,
            data_expiracao=dados.data_expiracao
        )

        return MemoriaRepository.criar(
            db,
            memoria
        )

    @staticmethod
    def listar_usuario(
        db: Session,
        id_usuario: int
    ) -> list[Memoria]:

        return MemoriaRepository.listar_ativas_usuario(
            db,
            id_usuario
        )

    @staticmethod
    def desativar(
        db: Session,
        id_memoria: int
    ) -> Memoria:

        memoria = MemoriaRepository.buscar_por_id(
            db,
            id_memoria
        )

        if memoria is None:
            raise ValueError(
                "Memória não encontrada."
            )

        return MemoriaRepository.desativar(
            db,
            memoria
        )