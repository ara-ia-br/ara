from datetime import datetime

from sqlalchemy.orm import Session

from app.models.lembrete import (
    Lembrete,
    StatusLembrete
)
from app.repositories.lembrete_repository import (
    LembreteRepository
)
from app.services.tarefa_service import TarefaService
from app.models.tarefa import StatusTarefa
from app.repositories.tarefa_repository import TarefaRepository

class LembreteService:

    @staticmethod
    def criar(
        db: Session,
        id_usuario: int,
        titulo: str,
        data_hora: datetime,
        descricao: str | None = None,
        recorrencia: str | None = None
    ) -> Lembrete:

        tarefa = TarefaService.criar(
            db=db,
            id_usuario=id_usuario,
            titulo=titulo,
            descricao=descricao,
            data_limite=data_hora
        )

        lembrete = Lembrete(
            id_usuario=id_usuario,
            id_tarefa=tarefa.id_tarefa,
            titulo=titulo,
            descricao=descricao,
            data_hora=data_hora,
            recorrencia=recorrencia,
            status=StatusLembrete.PENDENTE
        )

        return LembreteRepository.criar(
            db,
            lembrete
        )

    @staticmethod
    def listar(
        db: Session,
        id_usuario: int
    ) -> list[Lembrete]:

        return LembreteRepository.listar_por_usuario(
            db,
            id_usuario
        )

    @staticmethod
    def listar_pendentes(
            db: Session,
            id_usuario: int
    ) -> list[Lembrete]:

        return LembreteRepository.listar_pendentes(
            db,
            id_usuario
        )

    @staticmethod
    def cancelar(
            db: Session,
            id_usuario: int,
            titulo: str
    ) -> Lembrete:

        lembrete = (
            LembreteRepository.buscar_por_titulo(
                db,
                id_usuario,
                titulo
            )
        )

        if lembrete is None:
            raise ValueError(
                "Lembrete não encontrado."
            )

        lembrete.status = StatusLembrete.CANCELADA

        LembreteRepository.salvar(
            db,
            lembrete
        )

        tarefa = TarefaRepository.buscar_por_id(
            db,
            lembrete.id_tarefa
        )

        if tarefa is not None:
            tarefa.status = StatusTarefa.CANCELADA

            TarefaRepository.salvar(
                db,
                tarefa
            )

        return lembrete

    @staticmethod
    def concluir(
            db: Session,
            id_usuario: int,
            titulo: str
    ) -> Lembrete:

        lembrete = (
            LembreteRepository.buscar_por_titulo(
                db,
                id_usuario,
                titulo
            )
        )

        if lembrete is None:
            raise ValueError(
                "Lembrete não encontrado."
            )

        lembrete.status = StatusLembrete.CONCLUIDA

        LembreteRepository.salvar(
            db,
            lembrete
        )

        tarefa = TarefaRepository.buscar_por_id(
            db,
            lembrete.id_tarefa
        )

        if tarefa is not None:
            tarefa.status = StatusTarefa.CONCLUIDA
            tarefa.data_conclusao = datetime.now()

            TarefaRepository.salvar(
                db,
                tarefa
            )

        return lembrete

    @staticmethod
    def buscar_por_id(
            db: Session,
            id_lembrete: int
    ):

        lembrete = (
            LembreteRepository.buscar_por_id(
                db,
                id_lembrete
            )
        )

        if lembrete is None:
            raise ValueError(
                "Lembrete não encontrado."
            )

        return lembrete