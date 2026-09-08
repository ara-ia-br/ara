from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.schemas.auth import LoginRequest, LoginResponse
from app.services.auth_service import AuthService


router = APIRouter(
    prefix="/auth",
    tags=["Autenticação"]
)


@router.post(
    "/login",
    response_model=LoginResponse
)
def login(
    dados: LoginRequest,
    db: Session = Depends(get_db)
):

    resultado = AuthService.autenticar(
        db,
        dados.email,
        dados.senha
    )

    if resultado is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha inválidos."
        )

    return resultado



