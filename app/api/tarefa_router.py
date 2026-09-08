from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Response,
    status
)

from sqlalchemy.orm import Session

from app.database.connection import get_db

from app.models.tarefa import StatusTarefa

from app.schemas.tarefa import (
    TarefaCreate,
    TarefaResponse,
    TarefaUpdate
)

from app.services.tarefa_service import (
    TarefaService
)


router = APIRouter(
    prefix="/tarefas",
    tags=["Tarefas"]
)


@router.post(
    "",
    response_model=TarefaResponse,
    status_code=status.HTTP_201_CREATED
)
def criar_tarefa(
    dados: TarefaCreate,
    db: Session = Depends(get_db)
):

    try:

        return TarefaService.criar(
            db=db,
            id_usuario=dados.id_usuario,
            titulo=dados.titulo,
            descricao=dados.descricao,
            prioridade=dados.prioridade,
            data_limite=dados.data_limite
        )

    except ValueError as erro:

        raise HTTPException(
            status_code=400,
            detail=str(erro)
        )


@router.get(
    "/usuario/{id_usuario}",
    response_model=list[TarefaResponse]
)
def listar_tarefas_usuario(
    id_usuario: int,
    db: Session = Depends(get_db)
):

    return TarefaService.listar_por_usuario(
        db,
        id_usuario
    )


@router.get(
    "/usuario/{id_usuario}/status/{status_tarefa}",
    response_model=list[TarefaResponse]
)
def listar_tarefas_status(
    id_usuario: int,
    status_tarefa: StatusTarefa,
    db: Session = Depends(get_db)
):

    return TarefaService.listar_por_status(
        db,
        id_usuario,
        status_tarefa
    )


@router.get(
    "/{id_tarefa}",
    response_model=TarefaResponse
)
def buscar_tarefa(
    id_tarefa: int,
    db: Session = Depends(get_db)
):

    try:

        return TarefaService.buscar_por_id(
            db,
            id_tarefa
        )

    except ValueError as erro:

        raise HTTPException(
            status_code=404,
            detail=str(erro)
        )


@router.patch(
    "/{id_tarefa}",
    response_model=TarefaResponse
)
def editar_tarefa(
    id_tarefa: int,
    dados: TarefaUpdate,
    db: Session = Depends(get_db)
):

    try:

        return TarefaService.editar(
            db=db,
            id_tarefa=id_tarefa,
            titulo=dados.titulo,
            descricao=dados.descricao,
            prioridade=dados.prioridade,
            data_limite=dados.data_limite
        )

    except ValueError as erro:

        raise HTTPException(
            status_code=400,
            detail=str(erro)
        )


@router.patch(
    "/{id_tarefa}/iniciar",
    response_model=TarefaResponse
)
def iniciar_tarefa(
    id_tarefa: int,
    db: Session = Depends(get_db)
):

    try:

        return TarefaService.iniciar(
            db,
            id_tarefa
        )

    except ValueError as erro:

        raise HTTPException(
            status_code=400,
            detail=str(erro)
        )


@router.patch(
    "/{id_tarefa}/concluir",
    response_model=TarefaResponse
)
def concluir_tarefa(
    id_tarefa: int,
    db: Session = Depends(get_db)
):

    try:

        return TarefaService.concluir(
            db,
            id_tarefa
        )

    except ValueError as erro:

        raise HTTPException(
            status_code=400,
            detail=str(erro)
        )


@router.patch(
    "/{id_tarefa}/cancelar",
    response_model=TarefaResponse
)
def cancelar_tarefa(
    id_tarefa: int,
    db: Session = Depends(get_db)
):

    try:

        return TarefaService.cancelar(
            db,
            id_tarefa
        )

    except ValueError as erro:

        raise HTTPException(
            status_code=400,
            detail=str(erro)
        )


@router.delete(
    "/{id_tarefa}",
    status_code=status.HTTP_204_NO_CONTENT
)
def excluir_tarefa(
    id_tarefa: int,
    db: Session = Depends(get_db)
):

    try:

        TarefaService.excluir(
            db,
            id_tarefa
        )

        return Response(
            status_code=status.HTTP_204_NO_CONTENT
        )

    except ValueError as erro:

        raise HTTPException(
            status_code=404,
            detail=str(erro)
        )