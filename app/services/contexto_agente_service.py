from sqlalchemy.orm import Session

from app.models.contexto_agente import (
    ContextoAgente
)

from app.repositories.contexto_agente_repository import (
    ContextoAgenteRepository
)


class ContextoAgenteService:

    @staticmethod
    def obter(
        db: Session,
        id_usuario: int,
        id_conversa: int
    ) -> ContextoAgente:

        contexto = (
            ContextoAgenteRepository
            .buscar_por_conversa(
                db,
                id_conversa
            )
        )

        if contexto is not None:
            return contexto

        contexto = ContextoAgente(
            id_usuario=id_usuario,
            id_conversa=id_conversa
        )

        return (
            ContextoAgenteRepository.salvar(
                db,
                contexto
            )
        )


    @staticmethod
    def registrar_tarefa(
        db: Session,
        id_usuario: int,
        id_conversa: int,
        id_tarefa: int,
        ferramenta: str | None = None
    ) -> ContextoAgente:

        contexto = (
            ContextoAgenteService.obter(
                db=db,
                id_usuario=id_usuario,
                id_conversa=id_conversa
            )
        )

        contexto.ultima_tarefa_id = (
            id_tarefa
        )

        contexto.ultima_ferramenta = (
            ferramenta
        )

        return (
            ContextoAgenteRepository.salvar(
                db,
                contexto
            )
        )


    @staticmethod
    def obter_ultima_tarefa_id(
        db: Session,
        id_usuario: int,
        id_conversa: int
    ) -> int | None:

        contexto = (
            ContextoAgenteService.obter(
                db=db,
                id_usuario=id_usuario,
                id_conversa=id_conversa
            )
        )

        return contexto.ultima_tarefa_id