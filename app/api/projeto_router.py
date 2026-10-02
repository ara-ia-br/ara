from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.schemas.projeto import ProjetoCreate, ProjetoResponse, ProjetoUpdate
from app.services.projeto_service import ProjetoService


router = APIRouter(prefix="/projetos", tags=["Projetos"])


@router.post("", response_model=ProjetoResponse, status_code=status.HTTP_201_CREATED)
def criar_projeto(dados: ProjetoCreate, db: Session = Depends(get_db)):
    try:
        return ProjetoService.criar(db, dados.id_usuario, dados.nome, dados.descricao)
    except ValueError as erro:
        raise HTTPException(status_code=400, detail=str(erro))


@router.get("/usuario/{id_usuario}", response_model=list[ProjetoResponse])
def listar_projetos(id_usuario: int, db: Session = Depends(get_db)):
    return ProjetoService.listar_por_usuario(db, id_usuario)


@router.patch("/{id_projeto}", response_model=ProjetoResponse)
def editar_projeto(id_projeto: int, dados: ProjetoUpdate, db: Session = Depends(get_db)):
    try:
        return ProjetoService.editar(db, id_projeto, dados.nome, dados.descricao)
    except ValueError as erro:
        raise HTTPException(status_code=400, detail=str(erro))


@router.delete("/{id_projeto}", status_code=status.HTTP_204_NO_CONTENT)
def excluir_projeto(id_projeto: int, db: Session = Depends(get_db)):
    try:
        ProjetoService.excluir(db, id_projeto)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except ValueError as erro:
        raise HTTPException(status_code=404, detail=str(erro))


@router.patch("/{id_projeto}/conversas/{id_conversa}")
def adicionar_conversa(id_projeto: int, id_conversa: int, db: Session = Depends(get_db)):
    try:
        return ProjetoService.adicionar_conversa(db, id_projeto, id_conversa)
    except ValueError as erro:
        raise HTTPException(status_code=400, detail=str(erro))


@router.delete("/{id_projeto}/conversas/{id_conversa}")
def remover_conversa(id_projeto: int, id_conversa: int, db: Session = Depends(get_db)):
    try:
        return ProjetoService.remover_conversa(db, id_projeto, id_conversa)
    except ValueError as erro:
        raise HTTPException(status_code=400, detail=str(erro))
