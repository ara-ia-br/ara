from app.agent.tools.tarefa_tools import listar_tarefas_periodo
from app.agent.tool_registry import ToolRegistry

from app.agent.lembrete_tools import (
    criar_lembrete,
    listar_lembretes,
    cancelar_lembrete,
    concluir_lembrete,
    editar_lembrete,
    excluir_todos_lembretes
)

from app.agent.tools.nearby_tools import (
    consultar_lugares_proximos
)


from app.agent.tools.location_tools import (
    consultar_localizacao_atual
)

from app.agent.tools.route_tools import (
    consultar_rota,
)

from app.agent.tools.weather_tools import (
    consultar_clima_local,
)

from app.agent.tools.tarefa_tools import (
    criar_tarefa,
    listar_tarefas,
    iniciar_tarefa,
    consultar_tarefa,
    concluir_tarefa,
    cancelar_tarefa,
    reabrir_tarefa,
    editar_tarefa
)

from app.agent.lembrete_tools import (
    criar_lembrete,
    listar_lembretes,
    consultar_lembrete,
    cancelar_lembrete,
    concluir_lembrete,
    editar_lembrete,
    excluir_todos_lembretes
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
    ),

    ToolRegistry.registrar(
        "consultar_lembrete",
        consultar_lembrete
    )

    ToolRegistry.registrar(
        "cancelar_lembrete",
        cancelar_lembrete
    )

    ToolRegistry.registrar(
        "concluir_lembrete",
        concluir_lembrete
    )

    ToolRegistry.registrar(
        "editar_lembrete",
        editar_lembrete
    )

    ToolRegistry.registrar(
        "excluir_todos_lembretes",
        excluir_todos_lembretes
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
        "consultar_tarefa",
        consultar_tarefa
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


    # CLIMA
    ToolRegistry.registrar(
        "consultar_clima_local",
        consultar_clima_local
    )


    # ROTAS
    ToolRegistry.registrar(
        "consultar_rota",
        consultar_rota
    )

    # =========================================================
    # LOCALIZAÇÃO
    # =========================================================

    ToolRegistry.registrar(
        "consultar_localizacao_atual",
        consultar_localizacao_atual
    )


    # =========================================================
    # LUGARES PRÓXIMOS
    # =========================================================

    ToolRegistry.registrar(
        "consultar_lugares_proximos",
        consultar_lugares_proximos
    )