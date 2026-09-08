import bcrypt

from sqlalchemy.orm import Session

from app.repositories.usuario_repository import UsuarioRepository
from app.security.jwt import criar_token_acesso


class AuthService:

    @staticmethod
    def autenticar(
        db: Session,
        email: str,
        senha: str
    ) -> dict | None:

        usuario = UsuarioRepository.buscar_por_email(
            db,
            email
        )

        if usuario is None:
            return None

        if not usuario.ativo:
            return None

        senha_valida = bcrypt.checkpw(
            senha.encode("utf-8"),
            usuario.senha.encode("utf-8")
        )

        if not senha_valida:
            return None

        token = criar_token_acesso(
            usuario.id_usuario
        )

        return {
            "access_token": token,
            "token_type": "bearer",
            "id_usuario": usuario.id_usuario,
            "nome": usuario.nome,
            "email": usuario.email
        }