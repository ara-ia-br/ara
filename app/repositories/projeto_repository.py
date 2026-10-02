from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.projeto import Projeto


class ProjetoRepository:
    @staticmethod
    def criar(db: Session, projeto: Projeto) -> Projeto:
        db.add(projeto)
        db.commit()
        db.refresh(projeto)
        return projeto

    @staticmethod
    def buscar_por_id(db: Session, id_projeto: int) -> Projeto | None:
        return db.get(Projeto, id_projeto)

    @staticmethod
    def listar_por_usuario(db: Session, id_usuario: int) -> list[Projeto]:
        resultado = db.execute(
            select(Projeto)
            .where(Projeto.id_usuario == id_usuario)
            .order_by(Projeto.data_atualizacao.desc(), Projeto.id_projeto.desc())
        )
        return list(resultado.scalars().all())

    @staticmethod
    def salvar(db: Session, projeto: Projeto) -> Projeto:
        projeto.data_atualizacao = datetime.now()
        db.add(projeto)
        db.commit()
        db.refresh(projeto)
        return projeto

    @staticmethod
    def excluir(db: Session, projeto: Projeto) -> None:
        db.delete(projeto)
        db.commit()
