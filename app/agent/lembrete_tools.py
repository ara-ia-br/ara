from app.services.natural_time_service import NaturalTimeService
import re
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
    recorrencia: str | None = None,
    id_tarefa: int | None = None
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
        recorrencia=recorrencia,
        id_tarefa=id_tarefa
    )


    return {
        "sucesso": True,

        "id_lembrete":
            lembrete.id_lembrete,

        "id_tarefa":
            lembrete.id_tarefa,

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
# CONSULTAR LEMBRETE
# =========================================================

def consultar_lembrete(
    db: Session,
    id_usuario: int,
    titulo: str
) -> dict:

    titulo = titulo.strip()

    if not titulo:
        raise ValueError(
            "Informe qual lembrete deseja consultar."
        )

    lembretes = LembreteService.listar(
        db,
        id_usuario
    )

    def normalizar(valor: str) -> str:
        return re.sub(
            r"\s+",
            " ",
            valor.casefold()
        ).strip()

    titulo_normalizado = normalizar(titulo)

    lembrete_encontrado = None

    # Primeiro correspondência exata.
    for lembrete in lembretes:
        if normalizar(lembrete.titulo) == titulo_normalizado:
            lembrete_encontrado = lembrete
            break

    # Depois correspondência parcial.
    if lembrete_encontrado is None:
        for lembrete in lembretes:

            titulo_item = normalizar(
                lembrete.titulo
            )

            if (
                titulo_normalizado in titulo_item
                or titulo_item in titulo_normalizado
            ):
                lembrete_encontrado = lembrete
                break

    if lembrete_encontrado is None:
        return {
            "sucesso": True,
            "encontrado": False,
            "titulo_consultado": titulo
        }

    status = (
        lembrete_encontrado.status.value
        if hasattr(
            lembrete_encontrado.status,
            "value"
        )
        else str(lembrete_encontrado.status)
    )

    return {
        "sucesso": True,
        "encontrado": True,
        "id_lembrete":
            lembrete_encontrado.id_lembrete,
        "id_tarefa":
            lembrete_encontrado.id_tarefa,
        "titulo":
            lembrete_encontrado.titulo,
        "descricao":
            lembrete_encontrado.descricao,
        "data_hora": (
            lembrete_encontrado.data_hora.isoformat()
            if lembrete_encontrado.data_hora
            else None
        ),
        "recorrencia":
            lembrete_encontrado.recorrencia,
        "status": status
    }


# =========================================================
# CANCELAR LEMBRETE
# =========================================================


def cancelar_lembrete(
    db,
    id_usuario: int,
    titulo: str | None = None,
    id_lembrete: int | None = None
):
    """
    Cancela um lembrete.

    Ações contextuais devem usar id_lembrete.
    O título permanece apenas para compatibilidade.
    """

    if id_lembrete is not None:

        lembrete = LembreteService.buscar_por_id(
            db,
            id_lembrete
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

        resultado = LembreteService.cancelar(
            db=db,
            id_usuario=id_usuario,
            id_lembrete=lembrete.id_lembrete
        )

    else:

        if not titulo:
            raise ValueError(
                "Informe qual lembrete deseja cancelar."
            )

        resultado = LembreteService.cancelar(
            db=db,
            id_usuario=id_usuario,
            titulo=titulo
        )

    return {
        "id_lembrete": resultado.id_lembrete,
        "id_tarefa": resultado.id_tarefa,
        "titulo": resultado.titulo,
        "data_hora": resultado.data_hora.isoformat(),
        "status": (
            resultado.status.value
            if hasattr(resultado.status, "value")
            else str(resultado.status)
        )
    }

def concluir_lembrete(
    db,
    id_usuario: int,
    titulo: str | None = None,
    id_lembrete: int | None = None
):
    """
    Conclui um lembrete.

    Ações contextuais devem usar id_lembrete.
    O título permanece apenas para compatibilidade.
    """

    if id_lembrete is not None:

        lembrete = LembreteService.buscar_por_id(
            db,
            id_lembrete
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

        # O service atual trabalha por título.
        # Como já resolvemos o ID exato, usamos o título
        # desse registro específico.
        resultado = LembreteService.concluir(
            db=db,
            id_usuario=id_usuario,
            id_lembrete=lembrete.id_lembrete
        )

    else:

        if not titulo:
            raise ValueError(
                "Informe qual lembrete deseja concluir."
            )

        resultado = LembreteService.concluir(
            db=db,
            id_usuario=id_usuario,
            titulo=titulo
        )

    return {
        "id_lembrete": resultado.id_lembrete,
        "id_tarefa": resultado.id_tarefa,
        "titulo": resultado.titulo,
        "data_hora": resultado.data_hora.isoformat(),
        "status": (
            resultado.status.value
            if hasattr(resultado.status, "value")
            else str(resultado.status)
        )
    }

def editar_lembrete(
    db,
    id_usuario: int,
    titulo: str | None = None,
    nova_data_hora: str | None = None,
    novo_titulo: str | None = None,
    id_lembrete: int | None = None
):
    """
    Edita um lembrete existente.

    Prioridade de identificação:
    1. id_lembrete, quando fornecido pelo contexto;
    2. titulo, para compatibilidade com comandos explícitos.

    Aceita:
    - amanhã às 22h
    - sexta às 20h
    - 22h
    - 22:30
    """

    # ========================================================
    # RESOLVE O LEMBRETE
    # ========================================================

    lembrete = None

    # Caminho seguro para ações contextuais.
    if id_lembrete is not None:

        lembrete = LembreteService.buscar_por_id(
            db,
            id_lembrete
        )

        if lembrete.id_usuario != id_usuario:
            raise ValueError(
                "Lembrete não pertence ao usuário."
            )

    # Compatibilidade com chamadas antigas por título.
    else:

        if not titulo:
            raise ValueError(
                "Informe qual lembrete deseja editar."
            )

        lembretes = LembreteService.listar(
            db,
            id_usuario
        )

        titulo_normalizado = (
            titulo.lower().strip()
        )

        # Primeiro: correspondência exata.
        for item in lembretes:
            if (
                item.titulo.lower().strip()
                == titulo_normalizado
            ):
                lembrete = item
                break

        # Depois: correspondência parcial.
        if lembrete is None:
            for item in lembretes:

                titulo_item = (
                    item.titulo.lower().strip()
                )

                if (
                    titulo_normalizado in titulo_item
                    or titulo_item in titulo_normalizado
                ):
                    lembrete = item
                    break

        if lembrete is None:
            raise ValueError(
                f"Lembrete '{titulo}' não encontrado."
            )

    # ========================================================
    # PROTEÇÃO DE STATUS
    # ========================================================

    status_atual = (
        lembrete.status.value
        if hasattr(lembrete.status, "value")
        else str(lembrete.status)
    )

    if status_atual in {
        "CONCLUIDA",
        "CANCELADA"
    }:
        raise ValueError(
            "Não é possível editar um lembrete "
            f"com status {status_atual}."
        )

    # ========================================================
    # INTERPRETA NOVA DATA / HORÁRIO
    # ========================================================

    data_hora_final = None

    if nova_data_hora:

        # Primeiro tenta uma expressão temporal completa.
        data_hora_final = (
            NaturalTimeService.interpretar(
                nova_data_hora
            )
        )

        # Se recebeu somente horário, mantém a data atual.
        if data_hora_final is None:

            horario = re.search(
                r"(?<!\d)"
                r"([01]?\d|2[0-3])"
                r"(?:[:h](\d{2}))?"
                r"\s*(?:h|horas?)?"
                r"(?!\d)",
                nova_data_hora.lower()
            )

            if horario:

                hora = int(
                    horario.group(1)
                )

                minuto = int(
                    horario.group(2)
                    or 0
                )

                data_hora_final = (
                    lembrete.data_hora.replace(
                        hour=hora,
                        minute=minuto,
                        second=0,
                        microsecond=0
                    )
                )

        if data_hora_final is None:
            raise ValueError(
                "Não consegui identificar a nova "
                "data ou horário do lembrete."
            )

    if (
        data_hora_final is None
        and novo_titulo is None
    ):
        raise ValueError(
            "Informe o que deseja alterar "
            "no lembrete."
        )

    # ========================================================
    # PERSISTE
    # ========================================================

    lembrete = LembreteService.editar(
        db=db,
        id_lembrete=lembrete.id_lembrete,
        id_usuario=id_usuario,
        data_hora=data_hora_final,
        titulo=novo_titulo
    )

    return {
        "id_lembrete": lembrete.id_lembrete,
        "id_tarefa": lembrete.id_tarefa,
        "titulo": lembrete.titulo,
        "data_hora": lembrete.data_hora.isoformat(),
        "status": (
            lembrete.status.value
            if hasattr(lembrete.status, "value")
            else str(lembrete.status)
        )
    }

# =========================================================
# EXCLUIR TODOS OS LEMBRETES
# =========================================================

def excluir_todos_lembretes(
    db: Session,
    id_usuario: int
) -> dict:
    """
    Exclui fisicamente todos os lembretes do usuário.

    As tarefas vinculadas são preservadas.
    """

    quantidade = (
        LembreteService.excluir_todos(
            db=db,
            id_usuario=id_usuario
        )
    )

    return {
        "sucesso": True,
        "quantidade_excluida": quantidade
    }
