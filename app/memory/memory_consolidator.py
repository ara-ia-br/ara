import re
import unicodedata

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum

from sqlalchemy.orm import Session

from app.models.memoria import Memoria
from app.repositories.memoria_repository import MemoriaRepository


class MemoryConsolidationAction(str, Enum):
    CRIAR = "CRIAR"
    REFORCAR = "REFORCAR"
    ATUALIZAR = "ATUALIZAR"
    IGNORAR = "IGNORAR"


@dataclass
class MemoryConsolidationResult:
    acao: MemoryConsolidationAction
    memoria: Memoria | None = None
    memoria_anterior: Memoria | None = None
    similaridade: float = 0.0


class MemoryConsolidator:

    # =========================================================
    # CONFIGURAÇÃO
    # =========================================================

    LIMIAR_REFORCO = 0.80
    LIMIAR_RELACIONAMENTO = 0.35

    INCREMENTO_REFORCO = Decimal("5.00")
    IMPORTANCIA_MAXIMA = Decimal("100.00")

    STOPWORDS = {
        "a", "o", "as", "os",
        "um", "uma", "uns", "umas",
        "de", "da", "do", "das", "dos",
        "em", "no", "na", "nos", "nas",
        "para", "pra", "por",
        "com", "sem",
        "e", "ou", "mas", "que",
        "eu", "me", "meu", "minha",
        "meus", "minhas",
        "usuario",
        "usuário",
        "voce", "voces",
        "ele", "ela", "eles", "elas",
        "isso", "isto", "aquilo",
        "ser", "estar", "ter",
        "sou", "estou", "tenho"
    }

    # =========================================================
    # NORMALIZAÇÃO
    # =========================================================

    @staticmethod
    def _normalizar(
        texto: str
    ) -> str:

        if not texto:
            return ""

        texto = texto.lower().strip()

        texto = unicodedata.normalize(
            "NFD",
            texto
        )

        texto = "".join(
            caractere
            for caractere in texto
            if unicodedata.category(caractere) != "Mn"
        )

        texto = re.sub(
            r"[^\w\s]",
            " ",
            texto
        )

        texto = re.sub(
            r"\s+",
            " ",
            texto
        )

        return texto.strip()

    # =========================================================
    # PALAVRAS RELEVANTES
    # =========================================================

    @staticmethod
    def _palavras(
        texto: str
    ) -> set[str]:

        texto = MemoryConsolidator._normalizar(
            texto
        )

        palavras = set(
            re.findall(
                r"\b[a-z0-9]+\b",
                texto
            )
        )

        return {
            palavra
            for palavra in palavras
            if (
                palavra not in MemoryConsolidator.STOPWORDS
                and len(palavra) >= 3
            )
        }

    # =========================================================
    # SIMILARIDADE
    # =========================================================

    @staticmethod
    def _similaridade(
        texto_a: str,
        texto_b: str
    ) -> float:

        normalizado_a = (
            MemoryConsolidator._normalizar(
                texto_a
            )
        )

        normalizado_b = (
            MemoryConsolidator._normalizar(
                texto_b
            )
        )

        if not normalizado_a or not normalizado_b:
            return 0.0

        if normalizado_a == normalizado_b:
            return 1.0

        palavras_a = (
            MemoryConsolidator._palavras(
                texto_a
            )
        )

        palavras_b = (
            MemoryConsolidator._palavras(
                texto_b
            )
        )

        if not palavras_a or not palavras_b:
            return 0.0

        intersecao = palavras_a & palavras_b
        uniao = palavras_a | palavras_b

        if not uniao:
            return 0.0

        return len(intersecao) / len(uniao)

    # =========================================================
    # LOCALIZAR MELHOR CANDIDATA
    # =========================================================

    @staticmethod
    def _buscar_mais_similar(
        memorias: list[Memoria],
        conteudo: str
    ) -> tuple[Memoria | None, float]:

        melhor_memoria = None
        melhor_similaridade = 0.0

        for memoria in memorias:

            if not memoria.conteudo:
                continue

            similaridade = (
                MemoryConsolidator._similaridade(
                    memoria.conteudo,
                    conteudo
                )
            )

            if similaridade > melhor_similaridade:

                melhor_memoria = memoria
                melhor_similaridade = similaridade

        return (
            melhor_memoria,
            melhor_similaridade
        )

    # =========================================================
    # NORMALIZAR IMPORTÂNCIA
    # =========================================================

    @staticmethod
    def _normalizar_importancia(
        importancia
    ) -> Decimal:

        try:
            valor = Decimal(
                str(importancia)
            )

        except Exception:
            valor = Decimal("50.00")

        return max(
            Decimal("0.00"),
            min(
                MemoryConsolidator.IMPORTANCIA_MAXIMA,
                valor
            )
        )

    # =========================================================
    # CRIAR
    # =========================================================

    @staticmethod
    def _criar(
        db: Session,
        id_usuario: int,
        tipo: str,
        conteudo: str,
        importancia: Decimal
    ) -> Memoria:

        memoria = Memoria(
            id_usuario=id_usuario,
            tipo_memoria=tipo,
            conteudo=conteudo,
            importancia=importancia,
            ativa=True
        )

        return MemoriaRepository.criar(
            db,
            memoria
        )

    # =========================================================
    # REFORÇAR
    # =========================================================

    @staticmethod
    def _reforcar(
        db: Session,
        memoria: Memoria,
        nova_importancia: Decimal
    ) -> Memoria:

        importancia_atual = (
            MemoryConsolidator
            ._normalizar_importancia(
                memoria.importancia
            )
        )

        nova_importancia = (
            MemoryConsolidator
            ._normalizar_importancia(
                nova_importancia
            )
        )

        importancia_final = max(
            importancia_atual,
            nova_importancia
        )

        importancia_final = min(
            MemoryConsolidator.IMPORTANCIA_MAXIMA,
            importancia_final
            + MemoryConsolidator.INCREMENTO_REFORCO
        )

        return (
            MemoriaRepository
            .atualizar_importancia(
                db,
                memoria,
                importancia_final
            )
        )

    # =========================================================
    # CONSOLIDAR UMA MEMÓRIA
    # =========================================================

    @staticmethod
    def consolidar(
        db: Session,
        id_usuario: int,
        tipo: str,
        conteudo: str,
        importancia
    ) -> MemoryConsolidationResult:

        if id_usuario is None:
            return MemoryConsolidationResult(
                acao=MemoryConsolidationAction.IGNORAR
            )

        tipo = str(
            tipo or ""
        ).upper().strip()

        conteudo = str(
            conteudo or ""
        ).strip()

        if not tipo or not conteudo:
            return MemoryConsolidationResult(
                acao=MemoryConsolidationAction.IGNORAR
            )

        importancia = (
            MemoryConsolidator
            ._normalizar_importancia(
                importancia
            )
        )

        # =====================================================
        # 1. DUPLICATA EXATA
        # =====================================================

        memoria_exata = (
            MemoriaRepository
            .buscar_conteudo_por_tipo(
                db,
                id_usuario,
                tipo,
                conteudo
            )
        )

        if memoria_exata is not None:

            memoria_exata = (
                MemoryConsolidator._reforcar(
                    db,
                    memoria_exata,
                    importancia
                )
            )

            return MemoryConsolidationResult(
                acao=MemoryConsolidationAction.REFORCAR,
                memoria=memoria_exata,
                memoria_anterior=memoria_exata,
                similaridade=1.0
            )

        # =====================================================
        # 2. MEMÓRIAS DO MESMO TIPO
        # =====================================================

        memorias_existentes = (
            MemoriaRepository
            .listar_ativas_por_tipo(
                db,
                id_usuario,
                tipo
            )
        )

        memoria_similar, similaridade = (
            MemoryConsolidator
            ._buscar_mais_similar(
                memorias_existentes,
                conteudo
            )
        )

        # =====================================================
        # 3. MESMO FATO / REFORÇO
        # =====================================================

        if (
            memoria_similar is not None
            and similaridade
            >= MemoryConsolidator.LIMIAR_REFORCO
        ):

            memoria_reforcada = (
                MemoryConsolidator._reforcar(
                    db,
                    memoria_similar,
                    importancia
                )
            )

            return MemoryConsolidationResult(
                acao=MemoryConsolidationAction.REFORCAR,
                memoria=memoria_reforcada,
                memoria_anterior=memoria_similar,
                similaridade=similaridade
            )

        # =====================================================
        # IMPORTANTE:
        #
        # Similaridade lexical moderada NÃO significa que uma
        # informação substitui a outra.
        #
        # Exemplo:
        #
        # "Usuário estuda Engenharia de Software."
        # "Usuário estuda Banco de Dados."
        #
        # Elas podem coexistir.
        #
        # Contradição/substituição será implementada na próxima
        # evolução com classificação estruturada.
        # =====================================================

        # =====================================================
        # 4. CRIAR NOVA
        # =====================================================

        memoria_nova = (
            MemoryConsolidator._criar(
                db,
                id_usuario,
                tipo,
                conteudo,
                importancia
            )
        )

        return MemoryConsolidationResult(
            acao=MemoryConsolidationAction.CRIAR,
            memoria=memoria_nova,
            memoria_anterior=(
                memoria_similar
                if (
                    memoria_similar is not None
                    and similaridade
                    >= MemoryConsolidator
                    .LIMIAR_RELACIONAMENTO
                )
                else None
            ),
            similaridade=similaridade
        )