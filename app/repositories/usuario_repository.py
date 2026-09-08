from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.usuario import Usuario


class UsuarioRepository:

    @staticmethod
    def criar(db: Session, usuario: Usuario) -> Usuario:
        db.add(usuario)
        db.commit()
        db.refresh(usuario)

        return usuario


    @staticmethod
    def buscar_por_id(
            db: Session,
            id_usuario: int
    ) -> Usuario | None:
        return db.get(Usuario, id_usuario)



    @staticmethod
    def buscar_por_email(
            db: Session,
            email: str
    ) -> Usuario | None:
        result = db.execute(
            select(Usuario).where(
                Usuario.email == email
            )
        )

        return result.scalar_one_or_none()


    @staticmethod
    def listar(db: Session) -> list[Usuario]:
        result = db.execute(
            select(Usuario)
        )

        return list(result.scalars().all())