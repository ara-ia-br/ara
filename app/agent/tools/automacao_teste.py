def executar_automacao_teste(acao: str) -> str:
    """
    Simula a execução de uma automação externa.

    Neste primeiro teste não existe integração com
    nenhum serviço real. A função apenas representa
    o ponto onde futuramente uma API externa poderá
    ser chamada.
    """

    if not acao.strip():
        return "Nenhuma ação foi informada."

    return f"Automação executada: {acao}"