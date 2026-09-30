import re

from sqlalchemy.orm import Session

from app.agent.tool_registry import ToolRegistry
from app.ai.response_composer import ResponseComposer

from app.services.acao_pendente_service import (
    AcaoPendenteService
)

from app.services.chat_interaction_service import (
    ChatInteractionService
)


class PendingActionHandlerService:

    CONFIRMACOES = {
        "sim",
        "s",
        "confirmo",
        "confirmar",
        "pode",
        "pode sim",
        "sim pode",
        "sim, pode",
        "pode fazer",
        "pode excluir",
        "confirmo sim",
        "confirmo pode excluir",
        "tenho certeza"
    }

    RECUSAS = {
        "não",
        "nao",
        "n",
        "cancelar",
        "cancela",
        "cancele",
        "não quero",
        "nao quero",
        "deixa",
        "deixa pra lá",
        "deixa pra la",
        "não faça",
        "nao faca"
    }

    # =========================================================
    # NORMALIZAR
    # =========================================================

    @staticmethod
    def _normalizar(
        texto: str
    ) -> str:

        texto = (
            texto
            .strip()
            .lower()
        )

        texto = re.sub(
            r"[.!?,;:]+$",
            "",
            texto
        )

        return texto.strip()

    # =========================================================
    # PROCESSAR AÇÃO PENDENTE
    # =========================================================

    @staticmethod
    def processar(
        db: Session,
        id_usuario: int,
        id_conversa: int,
        conteudo: str
    ) -> dict | None:

        texto_normalizado = (
            PendingActionHandlerService
            ._normalizar(conteudo)
        )

        acao_pendente = (
            AcaoPendenteService.obter(
                id_usuario=id_usuario,
                id_conversa=id_conversa
            )
        )

        if acao_pendente is None:
            return None

        # =====================================================
        # USUÁRIO RECUSOU
        # =====================================================

        if (
            texto_normalizado
            in PendingActionHandlerService.RECUSAS
        ):

            AcaoPendenteService.cancelar(
                id_usuario=id_usuario,
                id_conversa=id_conversa
            )

            resposta = (
                acao_pendente.get(
                    "mensagem_cancelamento"
                )
                or (
                    "Certo, ação cancelada. "
                    "Nada foi alterado."
                )
            )

            ChatInteractionService.salvar_agent(
                db=db,
                id_conversa=id_conversa,
                conteudo_usuario=conteudo,
                resposta_ara=resposta
            )

            return {
                "id_conversa": id_conversa,
                "mensagem_usuario": conteudo,
                "resposta_ara": resposta,
                "modelo": "AGENT",
                "ferramenta": None,
                "tempo_processamento": 0
            }

        # =====================================================
        # NÃO É CONFIRMAÇÃO NEM RECUSA
        # =====================================================

        if (
            texto_normalizado
            not in PendingActionHandlerService.CONFIRMACOES
        ):
            return None

        # =====================================================
        # USUÁRIO CONFIRMOU
        # =====================================================

        acao = AcaoPendenteService.consumir(
            id_usuario=id_usuario,
            id_conversa=id_conversa
        )

        ferramenta = acao["ferramenta"]

        argumentos = dict(
            acao.get(
                "argumentos",
                {}
            )
        )

        argumentos["db"] = db
        argumentos["id_usuario"] = id_usuario

        try:

            resultado = ToolRegistry.executar(
                ferramenta,
                **argumentos
            )

            if not isinstance(
                resultado,
                dict
            ):
                raise ValueError(
                    "A ferramenta não retornou "
                    "um resultado válido."
                )

            if resultado.get(
                "sucesso"
            ) is not True:
                raise ValueError(
                    resultado.get(
                        "erro",
                        "A operação não foi concluída."
                    )
                )

            resposta = (
                ResponseComposer.formatar_tool(
                    ferramenta,
                    resultado
                )
            )

        except Exception as erro:

            print(
                "[AÇÃO PENDENTE] "
                f"Falha em {ferramenta}: {erro}"
            )

            resposta = (
                "Não consegui executar essa ação. "
                "Nenhum sucesso foi confirmado."
            )

            ChatInteractionService.salvar_agent(
                db=db,
                id_conversa=id_conversa,
                conteudo_usuario=conteudo,
                resposta_ara=resposta
            )

            return {
                "id_conversa": id_conversa,
                "mensagem_usuario": conteudo,
                "resposta_ara": resposta,
                "modelo": "AGENT",
                "ferramenta": ferramenta,
                "tempo_processamento": 0
            }

        ChatInteractionService.salvar_agent(
            db=db,
            id_conversa=id_conversa,
            conteudo_usuario=conteudo,
            resposta_ara=resposta
        )

        return {
            "id_conversa": id_conversa,
            "mensagem_usuario": conteudo,
            "resposta_ara": resposta,
            "modelo": "AGENT",
            "ferramenta": ferramenta,
            "tempo_processamento": 0
        }