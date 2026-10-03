from __future__ import annotations

import re
import unicodedata

from sqlalchemy.orm import Session

from app.agent.intent import (
    AgentDecision,
    TipoAcao
)
from app.models.mensagem import (
    Mensagem,
    RemetenteMensagem
)


class WeatherContextService:

    @staticmethod
    def _normalizar(
        texto: str | None
    ) -> str:

        valor = str(
            texto or ""
        ).strip().lower()

        valor = unicodedata.normalize(
            "NFD",
            valor
        )

        valor = "".join(
            caractere
            for caractere in valor
            if unicodedata.category(
                caractere
            ) != "Mn"
        )

        valor = re.sub(
            r"\s+",
            " ",
            valor
        )

        return valor.strip()


    @staticmethod
    def _ultimo_local_clima(
        db: Session,
        id_conversa: int
    ) -> str | None:

        mensagens = (
            db.query(Mensagem)
            .filter(
                Mensagem.id_conversa
                == id_conversa
            )
            .order_by(
                Mensagem.id_mensagem.desc()
            )
            .limit(20)
            .all()
        )

        for mensagem in mensagens:

            remetente = (
                mensagem.remetente.value
                if hasattr(
                    mensagem.remetente,
                    "value"
                )
                else str(
                    mensagem.remetente
                )
            )

            if remetente not in {
                "ARA",
                "JARVIS"
            }:
                continue

            conteudo = str(
                mensagem.conteudo
                or ""
            )

            match = re.search(
                r"^\s*Em\s+(.+?),\s+"
                r"est[áa]\s+fazendo\b",
                conteudo,
                flags=re.IGNORECASE
            )

            if match:

                return (
                    match.group(1)
                    .strip()
                )

        return None


    @classmethod
    def analisar(
        cls,
        mensagem: str,
        db: Session | None,
        id_conversa: int | None
    ) -> AgentDecision | None:

        if (
            db is None
            or id_conversa is None
        ):
            return None

        texto = cls._normalizar(
            mensagem
        )

        if not texto:
            return None


        ultimo_local = (
            cls._ultimo_local_clima(
                db=db,
                id_conversa=id_conversa
            )
        )


        ultimo_local = (
            cls._ultimo_local_clima(
                db=db,
                id_conversa=id_conversa
            )
        )

        # Sem contexto meteorológico anterior,
        # não tratamos frases curtas como continuação de clima.
        if not ultimo_local:
            return None


        # -----------------------------------------
        # "E EM ARAUCÁRIA?"
        # "E PARIS?"
        # -----------------------------------------

        match_local = re.fullmatch(
            r"(?:"
            r"(?:e\s+)?(?:em|no|na)\s+"
            r"|e\s+"
            r")"
            r"(.+?)"
            r"[?!.]*",
            texto
        )

        if match_local:

            local = (
                match_local
                .group(1)
                .strip(" ?!.,")
            )

            if local:

                return AgentDecision(
                    acao=TipoAcao.EXECUTAR,
                    ferramenta="consultar_clima_local",
                    argumentos={
                        "local": local,
                        "modo": "completo"
                    }
                )


        # -----------------------------------------
        # "E EM ARAUCÁRIA?"
        # -----------------------------------------

        match_local = re.fullmatch(
            r"(?:e\s+)?"
            r"(?:em|no|na)\s+"
            r"(.+?)"
            r"[?!.]*",
            texto
        )

        if match_local:

            local = (
                match_local
                .group(1)
                .strip(
                    " ?!.,"
                )
            )

            if local:

                return AgentDecision(
                    acao=TipoAcao.EXECUTAR,
                    ferramenta=
                        "consultar_clima_local",
                    argumentos={
                        "local": local,
                        "modo": "completo"
                    }
                )


        if not ultimo_local:
            return None


        # -----------------------------------------
        # GRÁFICO
        # -----------------------------------------

        if re.fullmatch(
            r"(?:me\s+)?"
            r"(?:de|da|mostra|mostre|"
            r"exibe|exiba)"
            r"(?:\s+o|\s+um)?\s+"
            r"grafico"
            r"(?:\s+entao)?"
            r"[?!.]*",
            texto
        ):

            return AgentDecision(
                acao=TipoAcao.EXECUTAR,
                ferramenta=
                    "consultar_clima_local",
                argumentos={
                    "local": ultimo_local,
                    "modo": "grafico"
                }
            )


        # -----------------------------------------
        # TABELA
        # -----------------------------------------

        if re.fullmatch(
            r"(?:me\s+)?"
            r"(?:passa|passe|mostra|mostre|"
            r"exibe|exiba|de)"
            r"(?:\s+a|\s+uma)?\s+"
            r"tabela"
            r"(?:\s+entao)?"
            r"[?!.]*",
            texto
        ):

            return AgentDecision(
                acao=TipoAcao.EXECUTAR,
                ferramenta=
                    "consultar_clima_local",
                argumentos={
                    "local": ultimo_local,
                    "modo": "tabela"
                }
            )


        return None