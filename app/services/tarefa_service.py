from datetime import datetime

from sqlalchemy.orm import Session

from app.models.tarefa import (
    StatusTarefa,
    Tarefa
)

from app.repositories.tarefa_repository import (
    TarefaRepository
)
from app.models.lembrete import Lembrete
from app.repositories.lembrete_repository import LembreteRepository


class TarefaService:

    @staticmethod
    def criar(
        db: Session,
        id_usuario: int,
        titulo: str,
        descricao: str | None = None,
        data_limite: datetime | None = None,
        prioridade: int = 3
    ) -> Tarefa:

        titulo = titulo.strip()

        if not titulo:
            raise ValueError(
                "O título da tarefa não pode ficar vazio."
            )

        if prioridade < 1 or prioridade > 5:
            raise ValueError(
                "A prioridade deve estar entre 1 e 5."
            )

        tarefa = Tarefa(
            id_usuario=id_usuario,
            titulo=titulo,
            descricao=descricao,
            prioridade=prioridade,
            status=StatusTarefa.PENDENTE,
            data_limite=data_limite
        )

        return TarefaRepository.criar(
            db,
            tarefa
        )

    @staticmethod
    def buscar_por_id(
        db: Session,
        id_tarefa: int
    ) -> Tarefa:

        tarefa = TarefaRepository.buscar_por_id(
            db,
            id_tarefa
        )

        if tarefa is None:
            raise ValueError(
                "Tarefa não encontrada."
            )

        return tarefa

    @staticmethod
    def listar_por_usuario(
        db: Session,
        id_usuario: int
    ) -> list[Tarefa]:

        return TarefaRepository.listar_por_usuario(
            db,
            id_usuario
        )

    @staticmethod
    def listar_por_status(
        db: Session,
        id_usuario: int,
        status: StatusTarefa
    ) -> list[Tarefa]:

        return TarefaRepository.listar_por_status(
            db,
            id_usuario,
            status
        )

    @staticmethod
    def iniciar(
        db: Session,
        id_tarefa: int
    ) -> Tarefa:

        tarefa = TarefaService.buscar_por_id(
            db,
            id_tarefa
        )

        if tarefa.status == StatusTarefa.CONCLUIDA:
            raise ValueError(
                "Uma tarefa concluída não pode ser iniciada."
            )

        if tarefa.status == StatusTarefa.CANCELADA:
            raise ValueError(
                "Uma tarefa cancelada não pode ser iniciada."
            )

        tarefa.status = StatusTarefa.EM_ANDAMENTO

        if tarefa.data_inicio is None:
            tarefa.data_inicio = datetime.now()

        return TarefaRepository.salvar(
            db,
            tarefa
        )

    @staticmethod
    def concluir(
        db: Session,
        id_tarefa: int
    ) -> Tarefa:

        tarefa = TarefaService.buscar_por_id(
            db,
            id_tarefa
        )

        if tarefa.status == StatusTarefa.CANCELADA:
            raise ValueError(
                "Uma tarefa cancelada não pode ser concluída."
            )

        tarefa.status = StatusTarefa.CONCLUIDA

        if tarefa.data_inicio is None:
            tarefa.data_inicio = datetime.now()

        tarefa.data_conclusao = datetime.now()

        return TarefaRepository.salvar(
            db,
            tarefa
        )

    @staticmethod
    def cancelar(
        db: Session,
        id_tarefa: int
    ) -> Tarefa:

        tarefa = TarefaService.buscar_por_id(
            db,
            id_tarefa
        )

        if tarefa.status == StatusTarefa.CONCLUIDA:
            raise ValueError(
                "Uma tarefa concluída não pode ser cancelada."
            )

        tarefa.status = StatusTarefa.CANCELADA

        return TarefaRepository.salvar(
            db,
            tarefa
        )

    @staticmethod
    def editar(
            db: Session,
            id_tarefa: int,
            titulo: str | None = None,
            descricao: str | None = None,
            prioridade: int | None = None,
            data_limite: datetime | None = None,
            remover_data_limite: bool = False
    ) -> Tarefa:

        tarefa = TarefaService.buscar_por_id(
            db,
            id_tarefa
        )

        if titulo is not None:

            titulo = titulo.strip()

            if not titulo:
                raise ValueError(
                    "O título não pode ficar vazio."
                )

            tarefa.titulo = titulo

        if descricao is not None:
            tarefa.descricao = descricao

        if prioridade is not None:

            if prioridade < 1 or prioridade > 5:
                raise ValueError(
                    "A prioridade deve estar entre 1 e 5."
                )

            tarefa.prioridade = prioridade

        if remover_data_limite:
            tarefa.data_limite = None

        elif data_limite is not None:
            tarefa.data_limite = data_limite

        return TarefaRepository.salvar(
            db,
            tarefa
        )
    @staticmethod
    def excluir(
        db: Session,
        id_tarefa: int
    ) -> None:

        tarefa = TarefaService.buscar_por_id(
            db,
            id_tarefa
        )

        TarefaRepository.excluir(
            db,
            tarefa
        )

    @staticmethod
    def buscar_por_titulo(
            db: Session,
            id_usuario: int,
            titulo: str
    ) -> Tarefa:

        titulo = titulo.strip()

        tarefa = TarefaRepository.buscar_por_titulo(db, id_usuario, titulo)

        if tarefa is None:
            raise ValueError(
                f"Tarefa '{titulo}' não encontrada."
            )
        return tarefa

    @staticmethod
    def reabrir(
            db: Session,
            id_tarefa: int
    ) -> Tarefa:

        tarefa = TarefaService.buscar_por_id(
            db,
            id_tarefa
        )

        tarefa.status = StatusTarefa.PENDENTE

        tarefa.data_inicio = None
        tarefa.data_conclusao = None

        return TarefaRepository.salvar(
            db,
            tarefa
        )

    @staticmethod
    def listar_por_periodo(
            db: Session,
            id_usuario: int,
            inicio: datetime,
            fim: datetime
    ) -> list[Tarefa]:

        return TarefaRepository.listar_por_periodo(
            db,
            id_usuario,
            inicio,
            fim
        )