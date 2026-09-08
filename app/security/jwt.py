from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt

from app.security.settings import setting


def criar_token_acesso(id_usuario: int) -> str:
    agora = datetime.now(timezone.utc)

    expiracao = agora + timedelta(
        minutes=setting.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": str(id_usuario),
        "iat": agora,
        "exp": expiracao
    }

    return jwt.encode(
        payload,
        setting.JWT_SECRET_KEY,
        algorithm=setting.JWT_ALGORITHM
    )


def obter_id_usuario_token(token: str) -> int:
    try:
        payload = jwt.decode(
            token,
            setting.JWT_SECRET_KEY,
            algorithms=[setting.JWT_ALGORITHM]
        )

        subject = payload.get("sub")

        if subject is None:
            raise ValueError("Token sem usuário.")

        return int(subject)

    except (JWTError, ValueError):
        raise ValueError("Token inválido ou expirado.")


