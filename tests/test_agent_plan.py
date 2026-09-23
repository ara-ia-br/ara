from datetime import datetime

from app.agent.agent import JarvisAgent
from app.agent.plan_resolver import AgentPlanResolver

def testar_planejar_tarefa_com_lembrete():
    plano = JarvisAgent.planejar(
        "crie uma tarefa chamada reuniao amanha as 19h e me lembre dela 30 minutos antes"
    )
    
    assert plano is not None
    assert len(plano.passos) == 2
    
    passo_tarefa = plano.passos[0]
    passo_lembrete = plano.passos[1]
    
    
    assert (
        passo_tarefa.decisao.ferramenta == "criar_tarefa"
    )
    
    assert (
        passo_tarefa.decisao.argumentos["titulo"] == "reuniao"
    )
    
    data_limite = datetime.fromisoformat(
        passo_tarefa.decisao.argumentos["data_limite"]
    )
    
    assert data_limite.hour == 19
    assert data_limite.minute == 0
    
    assert (
        passo_lembrete.decisao.ferramenta == "criar_lembrete"
    )
    
    assert passo_lembrete.depende_de == 0
    
    regra_data = (
        passo_lembrete.resolver_argumentos["data_hora"]
    )
    
    
    assert regra_data["resultado_de"] == 0
    assert regra_data["campo"] == "data_limite"
    assert regra_data["offset_minutos"] == -30
    
    
def testar_resolver_argumentos_lembrete():
    plano = JarvisAgent.planejar(
        "crie uma tarefa chamada reuniao amanha as 19h e me lembre dela 30 minutos antes"
    )
    
    assert plano is not None
    
    resultados = [
        {
            "id_tarefa": 123,
            "titulo": "reuniao",
            "data_limite": "2026-09-21T19:00:00-03:00"
        }
    ]
    
    
    argumentos = (
        AgentPlanResolver.resolver_argumentos(
            plano.passos[1], 
            resultados
        )
    )
    
    assert argumentos["id_tarefa"] == 123
    assert argumentos["titulo"] == "reuniao"
    
    assert (
        argumentos["data_hora"] == "2026-09-21T18:30:00-03:00"
    )
    
    
def test_mensagem_simples_nao_gera_plano():
    plano = JarvisAgent.planejar(
        "liste minhas tarefas"
    )
    
    assert plano is None


def test_planejar_duas_acoes_indepedentes():

    plano = JarvisAgent.planejar(
        "liste minhas tarefas "
        "e liste meus lembretes"
    )

    assert plano is not None
    assert len(plano.passos) == 2

    assert (plano.passos[0].decisao.ferramenta == "listar_tarefas")

    assert (plano.passos[1].decisao.ferramenta == "listar_lembretes")

    assert plano.passos[0].depende_de is None
    assert plano.passos[1].depende_de is None

def test_planejar_tres_acoes_independentes():

    plano = JarvisAgent.planejar(
        "liste minhas tarefas "
        "e liste meus lembretes "
        "e crie uma tarefa chamada revisar"
    )

    assert plano is not None
    assert len(plano.passos) == 3

    ferramentas = [
        passo.decisao.ferramenta
        for passo in plano.passos
    ]

    assert ferramentas == [
        "listar_tarefas",
        "listar_lembretes",
        "criar_tarefa"
    ]

    assert all(
        passo.depende_de is None
        for passo in plano.passos
    )