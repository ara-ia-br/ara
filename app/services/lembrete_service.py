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
from app.models.tarefa import Tarefa, StatusTarefa
from app.repositories.tarefa_repository import TarefaRepository

class LembreteService:

    @staticmethod
    def criar(
        db: Session,
        id_usuario: int,
        titulo: str,
        data_hora: datetime,
        descricao: str | None = None,
        recorrencia: str | None = None,
        id_tarefa: int | None = None
    ) -> Lembrete:

        # =====================================================
        # VÍNCULO COM TAREFA
        #
        # Se id_tarefa for informado, reutiliza uma tarefa já
        # existente. Caso contrário, mantém o comportamento
        # legado e cria uma tarefa para sustentar o lembrete.
        # =====================================================

        if id_tarefa is not None:

            tarefa = TarefaService.buscar_por_id(
                db,
                id_tarefa
            )

            if tarefa.id_usuario != id_usuario:
                raise ValueError(
                    "Tarefa não pertence ao usuário."
                )

        else:

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
        titulo: str | None = None,
        id_lembrete: int | None = None
    ):

        # Prioridade absoluta para ID.
        if id_lembrete is not None:
            lembrete = (
                LembreteRepository.buscar_por_id(
                    db,
                    id_lembrete
                )
            )
        else:
            if not titulo:
                raise ValueError(
                    "Informe o lembrete que deseja cancelar."
                )

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

        if lembrete.id_usuario != id_usuario:
            raise ValueError(
                "Lembrete não pertence ao usuário."
            )

        status = (
            lembrete.status.value
            if hasattr(lembrete.status, "value")
            else str(lembrete.status)
        )

        if status == "CANCELADA":
            raise ValueError(
                "Esse lembrete já está cancelado."
            )

        if status == "CONCLUIDA":
            raise ValueError(
                "Não é possível cancelar um lembrete concluído."
            )

        lembrete.status = (
            StatusLembrete.CANCELADA
        )

        LembreteRepository.salvar(
            db,
            lembrete
        )

        tarefa = (
            TarefaRepository.buscar_por_id(
                db,
                lembrete.id_tarefa
            )
        )

        if tarefa is not None:
            tarefa.status = (
                StatusTarefa.CANCELADA
            )

            TarefaRepository.salvar(
                db,
                tarefa
            )

        return lembrete



    @staticmethod
    def concluir(
        db: Session,
        id_usuario: int,
        titulo: str | None = None,
        id_lembrete: int | None = None
    ):

        # Prioridade absoluta para ID.
        if id_lembrete is not None:
            lembrete = (
                LembreteRepository.buscar_por_id(
                    db,
                    id_lembrete
                )
            )
        else:
            if not titulo:
                raise ValueError(
                    "Informe o lembrete que deseja concluir."
                )

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

        if lembrete.id_usuario != id_usuario:
            raise ValueError(
                "Lembrete não pertence ao usuário."
            )

        status = (
            lembrete.status.value
            if hasattr(lembrete.status, "value")
            else str(lembrete.status)
        )

        if status == "CONCLUIDA":
            raise ValueError(
                "Esse lembrete já está concluído."
            )

        if status == "CANCELADA":
            raise ValueError(
                "Não é possível concluir um lembrete cancelado."
            )

        lembrete.status = (
            StatusLembrete.CONCLUIDA
        )

        LembreteRepository.salvar(
            db,
            lembrete
        )

        tarefa = (
            TarefaRepository.buscar_por_id(
                db,
                lembrete.id_tarefa
            )
        )

        if tarefa is not None:

            tarefa.status = (
                StatusTarefa.CONCLUIDA
            )

            tarefa.data_conclusao = (
                datetime.now()
            )

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

    @staticmethod
    def editar(
        db: Session,
        id_lembrete: int,
        id_usuario: int,
        data_hora=None,
        titulo: str | None = None,
        descricao: str | None = None
    ):

        lembrete = (
            LembreteService.buscar_por_id(
                db,
                id_lembrete
            )
        )

        if lembrete.id_usuario != id_usuario:
            raise ValueError(
                "Esse lembrete não pertence ao usuário."
            )

        if titulo is not None:
            titulo = titulo.strip()

            if titulo:
                lembrete.titulo = titulo

        if descricao is not None:
            lembrete.descricao = descricao

        if data_hora is not None:
            lembrete.data_hora = data_hora

            # O lembrete possui uma tarefa obrigatoriamente vinculada.
            # Mantém o prazo da tarefa sincronizado quando possível.
            tarefa = db.get(
                Tarefa,
                lembrete.id_tarefa
            )

            if tarefa is not None:

                # Compatibilidade com possíveis nomes do campo
                # temporal existentes no model de tarefa.
                if hasattr(tarefa, "prazo"):
                    tarefa.prazo = data_hora

                elif hasattr(tarefa, "data_limite"):
                    tarefa.data_limite = data_hora

                elif hasattr(tarefa, "data_hora"):
                    tarefa.data_hora = data_hora

        db.add(lembrete)
        db.commit()
        db.refresh(lembrete)

        return lembrete

    @staticmethod
    def excluir_todos(
        db: Session,
        id_usuario: int
    ) -> int:
        """
        Exclui todos os lembretes do usuário.

        Não exclui as tarefas vinculadas.
        """

        return (
            LembreteRepository.excluir_todos_por_usuario(
                db=db,
                id_usuario=id_usuario
            )
        )
