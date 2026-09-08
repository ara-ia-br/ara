from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.contexto_agente import (
    ContextoAgente
)


class ContextoAgenteRepository:

    @staticmethod
    def buscar_por_conversa(
        db: Session,
        id_conversa: int
    ) -> ContextoAgente | None:

        resultado = db.execute(
            select(ContextoAgente)
            .where(
                ContextoAgente.id_conversa
                == id_conversa
            )
        )

        return (
            resultado
            .scalars()
            .first()
        )


    @staticmethod
    def salvar(
        db: Session,
        contexto: ContextoAgente
    ) -> ContextoAgente:

        db.add(contexto)

        db.commit()

        db.refresh(contexto)

        return contexto