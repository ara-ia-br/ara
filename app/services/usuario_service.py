import bcrypt

from sqlalchemy.orm import Session

from app.models.usuario import Usuario
from app.repositories.usuario_repository import UsuarioRepository
from app.schemas.usuario import UsuarioCreate


class UsuarioService:

    @staticmethod
    def criar(
        db: Session,
        dados: UsuarioCreate
    ) -> Usuario:

        usuario_existente = (
            UsuarioRepository.buscar_por_email(
                db,
                dados.email
            )
        )

        if usuario_existente:
            raise ValueError(
                "Já existe um usuário com este e-mail."
            )

        senha_bytes = dados.senha.encode("utf-8")

        if len(senha_bytes) > 72:
            raise ValueError(
                "A senha não pode possuir mais de 72 bytes."
            )

        senha_hash = bcrypt.hashpw(
            senha_bytes,
            bcrypt.gensalt()
        ).decode("utf-8")

        usuario = Usuario(
            nome=dados.nome,
            email=dados.email,
            senha=senha_hash
        )

        return UsuarioRepository.criar(
            db,
            usuario
        )

    @staticmethod
    def listar(
        db: Session
    ) -> list[Usuario]:

        return UsuarioRepository.listar(db)

    @staticmethod
    def buscar_por_id(
        db: Session,
        id_usuario: int
    ) -> Usuario | None:

        return UsuarioRepository.buscar_por_id(
            db,
            id_usuario
        )