from app.conversation.response_composer import ResponseComposer


def test_criar_tarefa_sem_bordao():

    resposta = ResponseComposer.compor(
        "criar_tarefa",
        {
            "titulo": "Estudar Python"
        }
    )

    assert resposta == 'Tarefa "Estudar Python" criada.'

    assert "Fechou" not in resposta
    assert "Boa!" not in resposta
    assert "Show!" not in resposta


def test_criar_lembrete_formata_data():
    resposta = ResponseComposer.compor(
        "criar_lembrete",
        {
            "titulo": "Estudar",
            "data_hora": "2026-09-25T18:30:00"
        }
    )

    assert resposta == (
        'Lembrete "Estudar" criado para '
        '25/09/2026 às 18:30.'
    )

def test_concluir_tarefa():
    resposta = ResponseComposer.compor(
        "concluir_tarefa",
        {
            "titulo": "Estudar Python"
        }
    )

    assert resposta == (
        'A tarefa "Estudar Python" foi concluída.'
    )

def test_listar_tarefas():

    resposta = ResponseComposer.compor(
        "listar_tarefas",
        {
            "tarefas": [
                {
                    "titulo": "Estudar",
                    "status": "PENDENTE"
                },
                {
                    "titulo": "Treinar",
                    "status": "CONCLUIDA"
                }
            ]
        }
    )

    assert "Estudar (pendente)" in resposta
    assert "Treinar (concluída)" in resposta


def test_consultar_prioridade():

    resposta = ResponseComposer.compor(
        "consultar_tarefa",
        {
            "titulo": "Estudar",
            "campo_consultado": "prioridade",
            "prioridade": 5
        }
    )

    assert resposta == (
        'A tarefa "Estudar" está com '
        "prioridade urgente."
    )


def test_fallback():
    resposta = ResponseComposer.compor(
        "ferramenta_desconhecida",
        {}
    )

    assert resposta == (
        "A ação foi concluída."
    )