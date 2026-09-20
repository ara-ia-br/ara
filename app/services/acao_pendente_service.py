from datetime import datetime, timedelta
from threading import RLock
from typing import Any


class AcaoPendenteService:
    """
    Armazena ações que aguardam confirmação do usuário.

    Chave:
        (id_usuario, id_conversa)

    Observação:
        armazenamento em memória adequado para a fase atual.
        Em ambiente distribuído, migrar para Redis/banco.
    """

    _acoes: dict[
        tuple[int, int],
        dict[str, Any]
    ] = {}

    _lock = RLock()

    TEMPO_EXPIRACAO_MINUTOS = 10


    @classmethod
    def registrar(
        cls,
        id_usuario: int,
        id_conversa: int,
        ferramenta: str,
        argumentos: dict | None = None,
        dominio: str | None = None,
        operacao: str | None = None,
        descricao: str | None = None,
        mensagem_confirmacao: str | None = None,
        mensagem_cancelamento: str | None = None
    ) -> None:

        chave = (
            id_usuario,
            id_conversa
        )

        agora = datetime.now()

        with cls._lock:

            cls._acoes[chave] = {
                "ferramenta": ferramenta,
                "argumentos": argumentos or {},

                # =============================================
                # METADADOS DA CONFIRMAÇÃO
                # =============================================
                "dominio": (
                    dominio.upper().strip()
                    if dominio
                    else None
                ),

                "operacao": (
                    operacao.upper().strip()
                    if operacao
                    else None
                ),

                "descricao": descricao,

                "mensagem_confirmacao":
                    mensagem_confirmacao,

                "mensagem_cancelamento":
                    mensagem_cancelamento,

                # =============================================
                # CONTROLE DE EXPIRAÇÃO
                # =============================================
                "criada_em": agora,

                "expira_em": (
                    agora
                    + timedelta(
                        minutes=cls.TEMPO_EXPIRACAO_MINUTOS
                    )
                )
            }


    @classmethod
    def obter(
        cls,
        id_usuario: int,
        id_conversa: int
    ) -> dict | None:

        chave = (
            id_usuario,
            id_conversa
        )

        with cls._lock:

            acao = cls._acoes.get(
                chave
            )

            if acao is None:
                return None

            if datetime.now() >= acao["expira_em"]:

                cls._acoes.pop(
                    chave,
                    None
                )

                return None

            return acao.copy()


    @classmethod
    def consumir(
        cls,
        id_usuario: int,
        id_conversa: int
    ) -> dict | None:
        """
        Retorna e remove a ação pendente.
        """

        chave = (
            id_usuario,
            id_conversa
        )

        with cls._lock:

            acao = cls._acoes.get(
                chave
            )

            if acao is None:
                return None

            if datetime.now() >= acao["expira_em"]:

                cls._acoes.pop(
                    chave,
                    None
                )

                return None

            return cls._acoes.pop(
                chave
            )


    @classmethod
    def cancelar(
        cls,
        id_usuario: int,
        id_conversa: int
    ) -> bool:

        chave = (
            id_usuario,
            id_conversa
        )

        with cls._lock:

            return (
                cls._acoes.pop(
                    chave,
                    None
                )
                is not None
            )


    @classmethod
    def existe(
        cls,
        id_usuario: int,
        id_conversa: int
    ) -> bool:

        return (
            cls.obter(
                id_usuario=id_usuario,
                id_conversa=id_conversa
            )
            is not None
        )
