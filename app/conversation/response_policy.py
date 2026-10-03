from dataclasses import dataclass
from enum import Enum

import re


class TamanhoResposta(str, Enum):
    CURTA = "CURTA"
    NORMAL = "NORMAL"
    DETALHADA = "DETALHADA"


class PoliticaMarkdown(str, Enum):
    MINIMO = "MINIMO"
    ESTRUTURADO = "ESTRUTURADO"


@dataclass(frozen=True)
class ResponseProfile:
    tamanho: TamanhoResposta
    markdown: PoliticaMarkdown
    max_tokens: int
    temperatura: float


class ResponsePolicy:

    # =====================================================
    # PEDIDOS EXPLÍCITOS DE RESPOSTA CURTA
    # =====================================================

    _PADROES_CURTOS = (
        r"\bresponda\s+(?:bem\s+)?curto\b",
        r"\bresposta\s+curta\b",
        r"\bseja\s+breve\b",
        r"\bem\s+uma\s+frase\b",
        r"\bsem\s+explica(?:ção|cao)\b",
        r"\bsó\s+(?:a\s+)?resposta\b",
        r"\bsomente\s+(?:a\s+)?resposta\b",
        r"\bresuma\b",
        r"\bresumo\s+rápido\b",
    )

    # =====================================================
    # PEDIDOS EXPLÍCITOS DE PROFUNDIDADE
    # =====================================================

    _PADROES_DETALHADOS = (
        r"\b(?:me\s+)?(?:explique|explica)\s+detalhadamente\b",
        r"\b(?:me\s+)?(?:explique|explica)\s+em\s+detalhes\b",
        r"\bpasso\s+a\s+passo\b",
        r"\bquero\s+detalhes\b",
        r"\bde\s+forma\s+detalhada\b",
        r"\bexplica(?:ção|cao)\s+completa\b",
        r"\banálise\s+completa\b",
        r"\banalise\s+completamente\b",
        r"\baprofund",
    )

    # =====================================================
    # SINAIS DE CONTEÚDO TÉCNICO
    # =====================================================

    _TERMOS_TECNICOS = (
        "traceback",
        "exception",
        "stack trace",
        "fastapi",
        "spring boot",
        "sqlalchemy",
        "mysql",
        "endpoint",
        "docker",
        "jwt",
        "api",
        "backend",
        "frontend",
        "python",
        "java",
        "javascript",
        "typescript",
        "react",
        "sql",
        "git",
        "github",
        "uvicorn",
        "pydantic",
    )

    @staticmethod
    def _normalizar(
        texto: str
    ) -> str:

        return (
            texto
            .strip()
            .lower()
        )

    @staticmethod
    def _corresponde(
        texto: str,
        padroes: tuple[str, ...]
    ) -> bool:

        return any(
            re.search(
                padrao,
                texto,
                flags=re.IGNORECASE
            )
            for padrao in padroes
        )

    @staticmethod
    def _aplicar_personalizacao(
            perfil_resposta: ResponseProfile,
            perfil_usuario
    ) -> ResponseProfile:

        if perfil_usuario is None:
            return perfil_resposta

        tamanho = perfil_resposta.tamanho
        markdown = perfil_resposta.markdown
        max_tokens = perfil_resposta.max_tokens
        temperatura = perfil_resposta.temperatura

        nivel_detalhe = getattr(
            perfil_usuario.nivel_detalhe,
            "value",
            perfil_usuario.nivel_detalhe
        )

        estilo_resposta = getattr(
            perfil_usuario.estilo_resposta,
            "value",
            perfil_usuario.estilo_resposta
        )

        nivel_detalhe = str(nivel_detalhe).upper()
        estilo_resposta = str(estilo_resposta).upper()

        # Preferência persistente de detalhamento
        if nivel_detalhe == "BAIXO":
            tamanho = TamanhoResposta.CURTA
            markdown = PoliticaMarkdown.MINIMO
            max_tokens = min(max_tokens, 350)

        elif nivel_detalhe == "ALTO":
            if tamanho == TamanhoResposta.CURTA:
                tamanho = TamanhoResposta.NORMAL
                max_tokens = max(max_tokens, 700)

            elif tamanho == TamanhoResposta.NORMAL:
                tamanho = TamanhoResposta.DETALHADA
                max_tokens = max(max_tokens, 1400)

        # Preferência por respostas diretas
        if estilo_resposta == "DIRETO":
            markdown = PoliticaMarkdown.MINIMO
            temperatura = min(temperatura, 0.4)

        return ResponseProfile(
            tamanho=tamanho,
            markdown=markdown,
            max_tokens=max_tokens,
            temperatura=temperatura
        )

    @staticmethod
    def _parece_tecnico(
            texto: str
    ) -> bool:

        texto_lower = texto.lower()

        # =====================================================
        # TERMOS TÉCNICOS COMO PALAVRAS/EXPRESSÕES COMPLETAS
        # =====================================================

        for termo in ResponsePolicy._TERMOS_TECNICOS:

            padrao = (
                rf"(?<!\w)"
                rf"{re.escape(termo)}"
                rf"(?!\w)"
            )

            if re.search(
                    padrao,
                    texto_lower,
                    flags=re.IGNORECASE
            ):
                return True

        # =====================================================
        # BLOCO DE CÓDIGO
        # =====================================================

        if "```" in texto:
            return True

        # =====================================================
        # SINAIS DE CÓDIGO
        # =====================================================

        if re.search(
                r"\b(?:class|def|import|from)\s+\w+",
                texto,
                flags=re.IGNORECASE
        ):
            return True

        return False

    # =====================================================
    # DEFINIR PERFIL
    # =====================================================


    @staticmethod
    def definir(
            mensagem: str,
            perfil_usuario=None,
            contexto_anterior: str | None = None
    ) -> ResponseProfile:
        texto = ResponsePolicy._normalizar(
            mensagem
        )

        texto = str(
            mensagem
            or ""
        ).strip()

        texto_lower = (
            texto.lower()
        )

        contexto_anterior = str(
            contexto_anterior
            or ""
        ).strip()

        texto_contextual = (
            f"{contexto_anterior}\n{texto}"
            if contexto_anterior
            else texto
        )

        # =================================================
        # PEDIDO EXPLÍCITO POR RESPOSTA DETALHADA
        # O pedido atual do usuário tem prioridade
        # =================================================

        if ResponsePolicy._corresponde(
                texto,
                ResponsePolicy._PADROES_DETALHADOS
        ):
            return ResponseProfile(
                tamanho=TamanhoResposta.DETALHADA,
                markdown=PoliticaMarkdown.ESTRUTURADO,
                max_tokens=2400,
                temperatura=0.45
            )

        # =================================================
        # PEDIDO EXPLÍCITO POR RESPOSTA CURTA
        # O pedido atual do usuário tem prioridade
        # =================================================

        if ResponsePolicy._corresponde(
                texto,
                ResponsePolicy._PADROES_CURTOS
        ):
            return ResponseProfile(
                tamanho=TamanhoResposta.CURTA,
                markdown=PoliticaMarkdown.MINIMO,
                max_tokens=220,
                temperatura=0.4
            )

        # =================================================
        # CONTEÚDO TÉCNICO
        # =================================================

        if ResponsePolicy._parece_tecnico(
                texto_contextual
        ):
            perfil_resposta = ResponseProfile(
                tamanho=TamanhoResposta.NORMAL,
                markdown=PoliticaMarkdown.ESTRUTURADO,
                max_tokens=1800,
                temperatura=0.35
            )

        # =================================================
        # CONVERSA NORMAL
        # =================================================

        else:
            perfil_resposta = ResponseProfile(
                tamanho=TamanhoResposta.CURTA,
                markdown=PoliticaMarkdown.MINIMO,
                max_tokens=350,
                temperatura=0.5
            )

        # =================================================
        # PERSONALIZAÇÃO PERSISTENTE DO USUÁRIO
        # =================================================

        return ResponsePolicy._aplicar_personalizacao(
            perfil_resposta=perfil_resposta,
            perfil_usuario=perfil_usuario
        )