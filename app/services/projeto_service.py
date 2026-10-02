from sqlalchemy.orm import Session

from app.models.conversa import Conversa
from app.models.projeto import Projeto
from app.repositories.conversa_repository import ConversaRepository
from app.repositories.projeto_repository import ProjetoRepository


class ProjetoService:
    @staticmethod
    def criar(db: Session, id_usuario: int, nome: str, descricao: str | None = None) -> Projeto:
        nome = nome.strip()
        if not nome:
            raise ValueError("O nome do projeto não pode ficar vazio.")

        projeto = Projeto(
            id_usuario=id_usuario,
            nome=nome,
            descricao=(descricao.strip() if descricao else None)
        )
        return ProjetoRepository.criar(db, projeto)

    @staticmethod
    def buscar_por_id(db: Session, id_projeto: int) -> Projeto:
        projeto = ProjetoRepository.buscar_por_id(db, id_projeto)
        if projeto is None:
            raise ValueError("Projeto não encontrado.")
        return projeto

    @staticmethod
    def listar_por_usuario(db: Session, id_usuario: int) -> list[Projeto]:
        return ProjetoRepository.listar_por_usuario(db, id_usuario)

    @staticmethod
    def editar(db: Session, id_projeto: int, nome: str | None, descricao: str | None) -> Projeto:
        projeto = ProjetoService.buscar_por_id(db, id_projeto)
        if nome is not None:
            nome = nome.strip()
            if not nome:
                raise ValueError("O nome do projeto não pode ficar vazio.")
            projeto.nome = nome
        if descricao is not None:
            projeto.descricao = descricao.strip() or None
        return ProjetoRepository.salvar(db, projeto)

    @staticmethod
    def excluir(db: Session, id_projeto: int) -> None:
        projeto = ProjetoService.buscar_por_id(db, id_projeto)
        ProjetoRepository.excluir(db, projeto)

    @staticmethod
    def adicionar_conversa(db: Session, id_projeto: int, id_conversa: int) -> Conversa:
        projeto = ProjetoService.buscar_por_id(db, id_projeto)
        conversa = ConversaRepository.buscar_por_id(db, id_conversa)
        if conversa is None:
            raise ValueError("Conversa não encontrada.")
        if conversa.id_usuario != projeto.id_usuario:
            raise ValueError("A conversa e o projeto pertencem a usuários diferentes.")

        conversa.id_projeto = projeto.id_projeto
        return ConversaRepository.salvar(db, conversa)

    @staticmethod
    def remover_conversa(db: Session, id_projeto: int, id_conversa: int) -> Conversa:
        projeto = ProjetoService.buscar_por_id(db, id_projeto)
        conversa = ConversaRepository.buscar_por_id(db, id_conversa)
        if conversa is None:
            raise ValueError("Conversa não encontrada.")
        if conversa.id_usuario != projeto.id_usuario:
            raise ValueError("A conversa e o projeto pertencem a usuários diferentes.")
        if conversa.id_projeto != projeto.id_projeto:
            raise ValueError("A conversa não está neste projeto.")

        conversa.id_projeto = None
        return ConversaRepository.salvar(db, conversa)
