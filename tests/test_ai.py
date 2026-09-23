from time import perf_counter

from app.ai.engine import ai_engine


mensagens = [
    {
        "role": "system",
        "content": (
            "Você é A.R.A, uma assistente "
            "pessoal inteligente e objetiva."
        )
    },
    {
        "role": "user",
        "content": (
            "Olá A.R.A. "
            "Se apresente em uma frase."
        )
    }
]


inicio = perf_counter()


try:

    resposta = ai_engine.gerar_resposta(
        mensagens
    )

    tempo = (
        perf_counter()
        - inicio
    )

    print("\nResposta:")
    print(resposta)

    print(
        f"\nTempo: {tempo:.2f}s"
    )


except Exception as erro:

    print(
        f"\nERRO: {type(erro).__name__}"
    )

    print(erro)