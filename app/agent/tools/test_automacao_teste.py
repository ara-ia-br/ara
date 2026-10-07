from app.agent.tools.automacao_teste import executar_automacao_teste
from app.agent.tool_registry import ToolRegistry
from app.agent.tools.register import registrar_tools
from app.agent.agent import JarvisAgent
from app.agent.intent import TipoAcao
from app.agent.tools.spotify_tools import executar_abrir_spotify


def test_executar_automacao_teste():
    resultado = executar_automacao_teste(
        "abrir o Spotify"
    )

    assert resultado == "Automação executada: abrir o Spotify"


def test_automacao_sem_acao():
    resultado = executar_automacao_teste("")

    assert resultado == "Nenhuma ação foi informada."


def test_automacao_pelo_tool_registry():
    ToolRegistry.registrar(
        "executar_automacao_teste",
        executar_automacao_teste
    )

    resultado = ToolRegistry.executar(
        "executar_automacao_teste",
        acao="abrir o Spotify"
    )

    assert resultado == "Automação executada: abrir o Spotify"

def test_automacao_registrada_pelo_register():
    registrar_tools()

    assert ToolRegistry.existe(
        "executar_automacao_teste"
    )

def test_automacao_registrada_no_registry():
    ToolRegistry.registrar(
        "automacao_teste",
        executar_automacao_teste
    )

    assert ToolRegistry.existe("automacao_teste")
    assert "automacao_teste" in ToolRegistry.listar()


def test_abrir_spotify_registrado():
    registrar_tools()

    assert ToolRegistry.existe(
        "abrir_spotify"
    )

def test_agente_decide_abrir_spotify():
    decisao = JarvisAgent.decidir(
        "abrir o Spotify"
    )

    assert decisao.acao == TipoAcao.EXECUTAR
    assert decisao.ferramenta == "abrir_spotify"