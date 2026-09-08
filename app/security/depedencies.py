from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.usuario import Usuario
from app.repositories.usuario_repository import UsuarioRepository
from app.security.jwt import obter_id_usuario_token


security = HTTPBearer()


def obter_usuario_atual(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> Usuario:

    token = credentials.credentials

    try:
        id_usuario = obter_id_usuario_token(token)

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    usuario = UsuarioRepository.buscar_por_id(
        db,
        id_usuario
    )

    if usuario is None or not usuario.ativo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não autorizado.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    return usuario