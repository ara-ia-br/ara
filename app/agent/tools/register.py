from app.agent.tools.tarefa_tools import listar_tarefas_periodo
from app.agent.tool_registry import ToolRegistry

from app.agent.lembrete_tools import (
    criar_lembrete,
    listar_lembretes,
    cancelar_lembrete,
    concluir_lembrete
)

from app.agent.tools.tarefa_tools import (
    criar_tarefa,
    listar_tarefas,
    iniciar_tarefa,
    concluir_tarefa,
    cancelar_tarefa,
    reabrir_tarefa,
    editar_tarefa
)

from app.agent.tools.tarefa_tools import (
    criar_tarefa,
    listar_tarefas,
    iniciar_tarefa,
    concluir_tarefa,
    cancelar_tarefa,
    reabrir_tarefa
)


def registrar_tools():

    # =========================================================
    # LEMBRETES
    # =========================================================

    ToolRegistry.registrar(
        "criar_lembrete",
        criar_lembrete
    )

    ToolRegistry.registrar(
        "listar_lembretes",
        listar_lembretes
    )

    ToolRegistry.registrar(
        "cancelar_lembrete",
        cancelar_lembrete
    )

    ToolRegistry.registrar(
        "concluir_lembrete",
        concluir_lembrete
    )


    # =========================================================
    # TAREFAS
    # =========================================================

    ToolRegistry.registrar(
        "criar_tarefa",
        criar_tarefa
    )

    ToolRegistry.registrar(
        "listar_tarefas",
        listar_tarefas
    )

    ToolRegistry.registrar(
        "iniciar_tarefa",
        iniciar_tarefa
    )

    ToolRegistry.registrar(
        "concluir_tarefa",
        concluir_tarefa
    )

    ToolRegistry.registrar(
        "cancelar_tarefa",
        cancelar_tarefa
    )

    ToolRegistry.registrar(
        "reabrir_tarefa",
        reabrir_tarefa
    )

    ToolRegistry.registrar(
        "editar_tarefa",
        editar_tarefa
    )

    ToolRegistry.registrar(
        "listar_tarefas_periodo",
        listar_tarefas_periodo
    )