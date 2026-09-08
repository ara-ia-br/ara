from pydantic import BaseModel, EmailStr

class LoginRequest(BaseModel):
    email: EmailStr
    senha: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    id_usuario: int
    nome: str
    email: EmailStr