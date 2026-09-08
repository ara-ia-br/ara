import re
from datetime import datetime

from sqlalchemy.orm import Session

from app.services.tarefa_service import TarefaService


# =========================================================
# NORMALIZAÇÃO DE TÍTULO
# =========================================================

def limpar_titulo(
    titulo: str
) -> str:

    if not titulo:
        raise ValueError(
            "O título da tarefa não foi informado."
        )

    titulo = titulo.strip()

    # Remove pontuação das extremidades
    titulo = titulo.strip(
        " ,.!?;:-"
    )

    # Remove expressões educadas no FINAL da frase
    titulo = re.sub(
        r"""
        [,\s]*
        (
            por\s+favor
            |
            por\s+gentileza
            |
            pra\s+mim
            |
            para\s+mim
            |
            pfv
            |
            obrigado
            |
            obrigada
            |
            obg
            |
            beleza
            |
            blz
        )
        [.!?]*$
        """,
        "",
        titulo,
        flags=(
            re.IGNORECASE
            | re.VERBOSE
        )
    )

    titulo = titulo.strip(
        " ,.!?;:-"
    )

    if not titulo:
        raise ValueError(
            "O título da tarefa não pode ficar vazio."
        )

    return titulo


# =========================================================
# CRIAR TAREFA
# =========================================================

def criar_tarefa(
    db: Session,
    id_usuario: int,
    titulo: str,
    descricao: str | None = None,
    prioridade: int = 3,
    data_limite: str | None = None
) -> dict:

    titulo = limpar_titulo(
        titulo
    )

    data_convertida = None

    if data_limite:

        try:

            data_convertida = (
                datetime.fromisoformat(
                    data_limite
                )
            )

        except ValueError:

            raise ValueError(
                "Data limite inválida."
            )

    tarefa = TarefaService.criar(
        db=db,
        id_usuario=id_usuario,
        titulo=titulo,
        descricao=descricao,
        prioridade=prioridade,
        data_limite=data_convertida
    )

    return {
        "sucesso": True,
        "id_tarefa": tarefa.id_tarefa,
        "titulo": tarefa.titulo,
        "descricao": tarefa.descricao,
        "prioridade": tarefa.prioridade,
        "status": tarefa.status.value,
        "data_limite": (
            tarefa.data_limite.isoformat()
            if tarefa.data_limite
            else None
        )
    }


# =========================================================
# LISTAR TAREFAS
# =========================================================

def listar_tarefas(
    db: Session,
    id_usuario: int
) -> dict:

    tarefas = (
        TarefaService.listar_por_usuario(
            db,
            id_usuario
        )
    )

    return {
        "sucesso": True,
        "tarefas": [
            {
                "id_tarefa":
                    tarefa.id_tarefa,

                "titulo":
                    tarefa.titulo,

                "descricao":
                    tarefa.descricao,

                "prioridade":
                    tarefa.prioridade,

                "status":
                    tarefa.status.value,

                "data_limite": (
                    tarefa.data_limite.isoformat()
                    if tarefa.data_limite
                    else None
                )
            }
            for tarefa in tarefas
        ]
    }


# =========================================================
# INICIAR TAREFA
# =========================================================

def iniciar_tarefa(
    db: Session,
    id_usuario: int,
    titulo: str
) -> dict:

    titulo = limpar_titulo(
        titulo
    )

    tarefa = (
        TarefaService.buscar_por_titulo(
            db,
            id_usuario,
            titulo
        )
    )

    tarefa = TarefaService.iniciar(
        db,
        tarefa.id_tarefa
    )

    return {
        "sucesso": True,
        "id_tarefa": tarefa.id_tarefa,
        "titulo": tarefa.titulo,
        "status": tarefa.status.value
    }


# =========================================================
# CONCLUIR TAREFA
# =========================================================

def concluir_tarefa(
    db: Session,
    id_usuario: int,
    titulo: str
) -> dict:

    titulo = limpar_titulo(
        titulo
    )

    tarefa = (
        TarefaService.buscar_por_titulo(
            db,
            id_usuario,
            titulo
        )
    )

    tarefa = TarefaService.concluir(
        db,
        tarefa.id_tarefa
    )

    return {
        "sucesso": True,
        "id_tarefa": tarefa.id_tarefa,
        "titulo": tarefa.titulo,
        "status": tarefa.status.value,
        "data_conclusao": (
            tarefa.data_conclusao.isoformat()
            if tarefa.data_conclusao
            else None
        )
    }


# =========================================================
# CANCELAR TAREFA
# =========================================================

def cancelar_tarefa(
    db: Session,
    id_usuario: int,
    titulo: str
) -> dict:

    titulo = limpar_titulo(
        titulo
    )

    tarefa = (
        TarefaService.buscar_por_titulo(
            db,
            id_usuario,
            titulo
        )
    )

    tarefa = TarefaService.cancelar(
        db,
        tarefa.id_tarefa
    )

    return {
        "sucesso": True,
        "id_tarefa": tarefa.id_tarefa,
        "titulo": tarefa.titulo,
        "status": tarefa.status.value
    }


# =========================================================
# REABRIR TAREFA
# =========================================================

def reabrir_tarefa(
    db: Session,
    id_usuario: int,
    titulo: str
) -> dict:

    titulo = limpar_titulo(
        titulo
    )

    tarefa = (
        TarefaService.buscar_por_titulo(
            db,
            id_usuario,
            titulo
        )
    )

    tarefa = TarefaService.reabrir(
        db,
        tarefa.id_tarefa
    )

    return {
        "sucesso": True,
        "id_tarefa": tarefa.id_tarefa,
        "titulo": tarefa.titulo,
        "status": tarefa.status.value
    }



def editar_tarefa(
    db: Session,
    id_usuario: int,
    titulo: str,
    novo_titulo: str | None = None,
    descricao: str | None = None,
    prioridade: int | None = None,
    data_limite: str | None = None,
    remover_data_limite: bool = False
) -> dict:

    titulo = limpar_titulo(
        titulo
    )

    if novo_titulo is not None:
        novo_titulo = limpar_titulo(
            novo_titulo
        )

    tarefa = TarefaService.buscar_por_titulo(
        db,
        id_usuario,
        titulo
    )

    data_convertida = None

    if data_limite is not None:

        try:

            data_convertida = datetime.fromisoformat(
                data_limite
            )

        except ValueError:

            raise ValueError(
                "A data limite informada é inválida."
            )

    tarefa = TarefaService.editar(
        db=db,
        id_tarefa=tarefa.id_tarefa,
        titulo=novo_titulo,
        descricao=descricao,
        prioridade=prioridade,
        data_limite=data_convertida,
        remover_data_limite=remover_data_limite
    )

    return {
        "sucesso": True,
        "id_tarefa": tarefa.id_tarefa,
        "titulo": tarefa.titulo,
        "descricao": tarefa.descricao,
        "prioridade": tarefa.prioridade,
        "status": tarefa.status.value,
        "data_limite": (
            tarefa.data_limite.isoformat()
            if tarefa.data_limite
            else None
        )
    }

def listar_tarefas_periodo(
    db: Session,
    id_usuario: int,
    inicio: str,
    fim: str
) -> dict:

    try:

        inicio_dt = datetime.fromisoformat(
            inicio
        )

        fim_dt = datetime.fromisoformat(
            fim
        )

    except ValueError:

        raise ValueError(
            "Período inválido."
        )

    tarefas = TarefaService.listar_por_periodo(
        db,
        id_usuario,
        inicio_dt,
        fim_dt
    )

    return {
        "sucesso": True,
        "tarefas": [
            {
                "id_tarefa": tarefa.id_tarefa,
                "titulo": tarefa.titulo,
                "status": tarefa.status.value,
                "prioridade": tarefa.prioridade,
                "data_limite": (
                    tarefa.data_limite.isoformat()
                    if tarefa.data_limite
                    else None
                )
            }
            for tarefa in tarefas
        ]
    }