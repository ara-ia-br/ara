from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.schemas.agenda import LembreteCreate, LembreteResponse, LembreteUpdate


router = APIRouter(prefix="/agenda", tags=["Agenda"])


COLUNAS = """
    id_lembrete,
    id_usuario,
    id_tarefa,
    titulo,
    descricao,
    data_hora,
    recorrencia,
    status,
    data_criacao
"""


def buscar_lembrete(db: Session, id_lembrete: int, id_usuario: int):
    resultado = db.execute(
        text(f"SELECT {COLUNAS} FROM lembrete WHERE id_lembrete = :id AND id_usuario = :usuario"),
        {"id": id_lembrete, "usuario": id_usuario},
    ).mappings().first()
    return resultado


@router.get("/usuario/{id_usuario}", response_model=list[LembreteResponse])
def listar_agenda(id_usuario: int, db: Session = Depends(get_db)):
    resultado = db.execute(
        text(f"""
            SELECT {COLUNAS}
            FROM lembrete
            WHERE id_usuario = :usuario
            ORDER BY data_hora ASC, id_lembrete ASC
        """),
        {"usuario": id_usuario},
    ).mappings().all()
    return list(resultado)


@router.post("", response_model=LembreteResponse, status_code=status.HTTP_201_CREATED)
def criar_evento(dados: LembreteCreate, db: Session = Depends(get_db)):
    if not dados.titulo.strip():
        raise HTTPException(status_code=400, detail="O título não pode ficar vazio.")

    resultado = db.execute(
        text("""
            INSERT INTO lembrete
                (id_usuario, titulo, descricao, data_hora, recorrencia, status)
            VALUES
                (:usuario, :titulo, :descricao, :data_hora, :recorrencia, 'PENDENTE')
        """),
        {
            "usuario": dados.id_usuario,
            "titulo": dados.titulo.strip(),
            "descricao": dados.descricao.strip() if dados.descricao else None,
            "data_hora": dados.data_hora,
            "recorrencia": dados.recorrencia.strip() if dados.recorrencia else None,
        },
    )
    db.commit()
    return buscar_lembrete(db, resultado.lastrowid, dados.id_usuario)


@router.patch("/{id_lembrete}", response_model=LembreteResponse)
def editar_evento(
    id_lembrete: int,
    dados: LembreteUpdate,
    id_usuario: int,
    db: Session = Depends(get_db),
):
    atual = buscar_lembrete(db, id_lembrete, id_usuario)
    if atual is None:
        raise HTTPException(status_code=404, detail="Evento não encontrado.")

    campos = []
    valores = {"id": id_lembrete, "usuario": id_usuario}

    if dados.titulo is not None:
        if not dados.titulo.strip():
            raise HTTPException(status_code=400, detail="O título não pode ficar vazio.")
        campos.append("titulo = :titulo")
        valores["titulo"] = dados.titulo.strip()
    if dados.descricao is not None:
        campos.append("descricao = :descricao")
        valores["descricao"] = dados.descricao.strip() or None
    if dados.data_hora is not None:
        campos.append("data_hora = :data_hora")
        valores["data_hora"] = dados.data_hora
    if dados.recorrencia is not None:
        campos.append("recorrencia = :recorrencia")
        valores["recorrencia"] = dados.recorrencia.strip() or None
    if dados.status is not None:
        if dados.status not in {"PENDENTE", "EM_ANDAMENTO", "CONCLUIDA", "CANCELADA"}:
            raise HTTPException(status_code=400, detail="Status de evento inválido.")
        campos.append("status = :status")
        valores["status"] = dados.status

    if campos:
        db.execute(
            text(f"UPDATE lembrete SET {', '.join(campos)} WHERE id_lembrete = :id AND id_usuario = :usuario"),
            valores,
        )
        db.commit()

    return buscar_lembrete(db, id_lembrete, id_usuario)


@router.delete("/{id_lembrete}", status_code=status.HTTP_204_NO_CONTENT)
def excluir_evento(id_lembrete: int, id_usuario: int, db: Session = Depends(get_db)):
    atual = buscar_lembrete(db, id_lembrete, id_usuario)
    if atual is None:
        raise HTTPException(status_code=404, detail="Evento não encontrado.")

    db.execute(
        text("DELETE FROM lembrete WHERE id_lembrete = :id AND id_usuario = :usuario"),
        {"id": id_lembrete, "usuario": id_usuario},
    )
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
