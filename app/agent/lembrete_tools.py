from datetime import datetime

from sqlalchemy.orm import Session

from app.services.lembrete_service import (
    LembreteService
)


# =========================================================
# CRIAR LEMBRETE
# =========================================================

def criar_lembrete(
    db: Session,
    id_usuario: int,
    titulo: str,
    data_hora: str,
    descricao: str | None = None,
    recorrencia: str | None = None
) -> dict:

    titulo = titulo.strip()

    if not titulo:
        raise ValueError(
            "O título do lembrete não pode ficar vazio."
        )

    try:

        data_convertida = datetime.fromisoformat(
            data_hora
        )

    except (
        ValueError,
        TypeError
    ):

        raise ValueError(
            "Data do lembrete inválida."
        )


    lembrete = LembreteService.criar(
        db=db,
        id_usuario=id_usuario,
        titulo=titulo,
        data_hora=data_convertida,
        descricao=descricao,
        recorrencia=recorrencia
    )


    return {
        "sucesso": True,

        "id_lembrete":
            lembrete.id_lembrete,

        "titulo":
            lembrete.titulo,

        "descricao":
            lembrete.descricao,

        "data_hora": (
            lembrete.data_hora.isoformat()
            if lembrete.data_hora
            else None
        ),

        "recorrencia":
            lembrete.recorrencia,

        "status":
            lembrete.status.value
    }


# =========================================================
# LISTAR LEMBRETES
# =========================================================

def listar_lembretes(
    db: Session,
    id_usuario: int
) -> dict:

    lembretes = (
        LembreteService.listar_pendentes(
            db,
            id_usuario
        )
    )


    return {
        "sucesso": True,

        "lembretes": [

            {
                "id_lembrete":
                    lembrete.id_lembrete,

                "titulo":
                    lembrete.titulo,

                "descricao":
                    lembrete.descricao,

                "data_hora": (
                    lembrete.data_hora.isoformat()
                    if lembrete.data_hora
                    else None
                ),

                "recorrencia":
                    lembrete.recorrencia,

                "status":
                    lembrete.status.value
            }

            for lembrete in lembretes
        ]
    }


# =========================================================
# CANCELAR LEMBRETE
# =========================================================

def cancelar_lembrete(
    db: Session,
    id_usuario: int,
    titulo: str
) -> dict:

    titulo = titulo.strip()

    if not titulo:

        raise ValueError(
            "Informe qual lembrete deseja cancelar."
        )


    lembrete = (
        LembreteService.cancelar(
            db=db,
            id_usuario=id_usuario,
            titulo=titulo
        )
    )


    return {
        "sucesso": True,

        "id_lembrete":
            lembrete.id_lembrete,

        "titulo":
            lembrete.titulo,

        "data_hora": (
            lembrete.data_hora.isoformat()
            if lembrete.data_hora
            else None
        ),

        "status":
            lembrete.status.value
    }


# =========================================================
# CONCLUIR LEMBRETE
# =========================================================

def concluir_lembrete(
    db: Session,
    id_usuario: int,
    titulo: str
) -> dict:

    titulo = titulo.strip()

    if not titulo:

        raise ValueError(
            "Informe qual lembrete deseja concluir."
        )


    lembrete = (
        LembreteService.concluir(
            db=db,
            id_usuario=id_usuario,
            titulo=titulo
        )
    )


    return {
        "sucesso": True,

        "id_lembrete":
            lembrete.id_lembrete,

        "titulo":
            lembrete.titulo,

        "data_hora": (
            lembrete.data_hora.isoformat()
            if lembrete.data_hora
            else None
        ),

        "status":
            lembrete.status.value
    }