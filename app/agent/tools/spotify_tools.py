from app.automation.executor_local import abrir_spotify


def executar_abrir_spotify(
    db=None,
    id_usuario=None
    ) -> dict:
      """
      Ferramenta da A.R.A. para solicitar a abertura do Spotify.
      """

      return abrir_spotify()