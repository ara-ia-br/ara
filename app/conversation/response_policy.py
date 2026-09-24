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
        r"\bexplique\s+detalhadamente\b",
        r"\bexplique\s+em\s+detalhes\b",
        r"\bpasso\s+a\s+passo\b",
        r"\bquero\s+detalhes\b",
        r"\bde\s+forma\s+detalhada\b",
        r"\bexplicação\s+completa\b",
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
        mensagem: str
    ) -> ResponseProfile:

        texto = ResponsePolicy._normalizar(
            mensagem
        )

        # -------------------------------------------------
        # PEDIDO EXPLÍCITO DE DETALHAMENTO
        # -------------------------------------------------

        if ResponsePolicy._corresponde(
            texto,
            ResponsePolicy._PADROES_DETALHADOS
        ):

            return ResponseProfile(
                tamanho=TamanhoResposta.DETALHADA,
                markdown=PoliticaMarkdown.ESTRUTURADO,
                max_tokens=1400,
                temperatura=0.45
            )

        # -------------------------------------------------
        # PEDIDO EXPLÍCITO DE CONCISÃO
        # -------------------------------------------------

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

        # -------------------------------------------------
        # CONTEÚDO TÉCNICO
        # -------------------------------------------------

        if ResponsePolicy._parece_tecnico(
            mensagem
        ):

            return ResponseProfile(
                tamanho=TamanhoResposta.NORMAL,
                markdown=PoliticaMarkdown.ESTRUTURADO,
                max_tokens=1000,
                temperatura=0.35
            )

        # -------------------------------------------------
        # PADRÃO DA NOVA A.R.A.
        # -------------------------------------------------
        #
        # Respostas conversacionais devem ser curtas,
        # naturais e sem Markdown desnecessário.
        # -------------------------------------------------

        return ResponseProfile(
            tamanho=TamanhoResposta.CURTA,
            markdown=PoliticaMarkdown.MINIMO,
            max_tokens=350,
            temperatura=0.5
        )