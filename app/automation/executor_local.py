import os


def abrir_spotify() -> dict:
    """
    Solicita ao sistema operacional a abertura do Spotify.

    A ação é local e não depende do ChatService.
    """

    try:
        os.startfile("spotify:")

        return {
            "sucesso": True,
            "status": "solicitado",
            "mensagem": "O Spotify foi solicitado para abertura.",
        }

    except OSError as erro:
        return {
            "sucesso": False,
            "status": "falha",
            "mensagem": "Não foi possível solicitar a abertura do Spotify.",
            "codigo": "ERRO_ABRIR_SPOTIFY",
        }