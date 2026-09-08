import re
import unicodedata

from sqlalchemy.orm import Session

from app.models.entidade_contextual import (
    EntidadeContextual
)

from app.repositories.entidade_contextual_repository import (
    EntidadeContextualRepository
)


class EntidadeContextualService:

    # =========================================================
    # NORMALIZAR TEXTO
    # =========================================================

    @staticmethod
    def _normalizar_texto(
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
            if unicodedata.category(caractere)
            != "Mn"
        )

        texto = re.sub(
            r"\s+",
            " ",
            texto
        )

        return texto.strip()


    # =========================================================
    # VERIFICAR EXPRESSÃO COMPLETA
    # =========================================================

    @staticmethod
    def _contem_expressao(
        texto: str,
        expressao: str
    ) -> bool:

        texto = (
            EntidadeContextualService
            ._normalizar_texto(
                texto
            )
        )

        expressao = (
            EntidadeContextualService
            ._normalizar_texto(
                expressao
            )
        )

        return (
            re.search(
                rf"(?<!\w)"
                rf"{re.escape(expressao)}"
                rf"(?!\w)",
                texto
            )
            is not None
        )


    # =========================================================
    # REGISTRAR ENTIDADE
    # =========================================================

    @staticmethod
    def registrar(
        db: Session,
        id_usuario: int,
        id_conversa: int,
        tipo_entidade: str,
        id_entidade: int,
        titulo: str | None = None
    ) -> EntidadeContextual:

        if id_usuario is None:
            raise ValueError(
                "id_usuario não informado ao contexto."
            )

        if id_conversa is None:
            raise ValueError(
                "id_conversa não informado ao contexto."
            )

        if id_entidade is None:
            raise ValueError(
                "id_entidade não informado ao contexto."
            )

        if not tipo_entidade:
            raise ValueError(
                "tipo_entidade não informado."
            )

        tipo_entidade = (
            tipo_entidade
            .strip()
            .upper()
        )

        titulo_limpo = None

        if titulo:

            titulo_limpo = titulo.strip()

            if not titulo_limpo:
                titulo_limpo = None

        entidade = EntidadeContextual(
            id_usuario=id_usuario,
            id_conversa=id_conversa,
            tipo_entidade=tipo_entidade,
            id_entidade=id_entidade,
            titulo=titulo_limpo,
            ordem_contexto=1
        )

        return (
            EntidadeContextualRepository.criar(
                db,
                entidade
            )
        )


    # =========================================================
    # LISTAR MENÇÕES RECENTES
    # =========================================================

    @staticmethod
    def listar_tarefas_recentes(
        db: Session,
        id_usuario: int,
        id_conversa: int,
        limite: int = 20
    ) -> list[EntidadeContextual]:

        return (
            EntidadeContextualRepository
            .listar_recentes(
                db=db,
                id_usuario=id_usuario,
                id_conversa=id_conversa,
                tipo_entidade="TAREFA",
                limite=limite
            )
        )


    # =========================================================
    # LISTAR TAREFAS ÚNICAS
    # Ordem cronológica de menção recente
    # =========================================================

    @staticmethod
    def listar_tarefas_unicas(
        db: Session,
        id_usuario: int,
        id_conversa: int,
        limite: int = 50
    ) -> list[EntidadeContextual]:

        entidades = (
            EntidadeContextualService
            .listar_tarefas_recentes(
                db=db,
                id_usuario=id_usuario,
                id_conversa=id_conversa,
                limite=limite
            )
        )

        ids_encontrados = set()

        tarefas_unicas = []

        for entidade in entidades:

            if (
                entidade.id_entidade
                in ids_encontrados
            ):
                continue

            ids_encontrados.add(
                entidade.id_entidade
            )

            tarefas_unicas.append(
                entidade
            )

        return tarefas_unicas


    # =========================================================
    # FOCO ATUAL
    # =========================================================

    @staticmethod
    def obter_foco_atual(
        db: Session,
        id_usuario: int,
        id_conversa: int
    ) -> EntidadeContextual | None:

        return (
            EntidadeContextualRepository
            .buscar_foco_atual(
                db=db,
                id_usuario=id_usuario,
                id_conversa=id_conversa,
                tipo_entidade="TAREFA"
            )
        )


    # =========================================================
    # FOCO ANTERIOR
    # =========================================================

    @staticmethod
    def obter_foco_anterior(
        db: Session,
        id_usuario: int,
        id_conversa: int
    ) -> EntidadeContextual | None:

        return (
            EntidadeContextualRepository
            .buscar_foco_anterior(
                db=db,
                id_usuario=id_usuario,
                id_conversa=id_conversa,
                tipo_entidade="TAREFA"
            )
        )


    # =========================================================
    # PRIMEIRA / SEGUNDA / TERCEIRA
    #
    # Continua usando ordem cronológica,
    # não ordem de foco.
    # =========================================================

    @staticmethod
    def obter_por_posicao(
        db: Session,
        id_usuario: int,
        id_conversa: int,
        posicao: int
    ) -> EntidadeContextual | None:

        if posicao < 1:
            return None

        tarefas = (
            EntidadeContextualService
            .listar_tarefas_unicas(
                db=db,
                id_usuario=id_usuario,
                id_conversa=id_conversa,
                limite=100
            )
        )

        tarefas = list(
            reversed(
                tarefas
            )
        )

        if posicao > len(tarefas):
            return None

        return tarefas[
            posicao - 1
        ]


    # =========================================================
    # BUSCAR POR TÍTULO
    # =========================================================

    @staticmethod
    def buscar_por_titulo(
        db: Session,
        id_usuario: int,
        id_conversa: int,
        texto: str
    ) -> EntidadeContextual | None:

        if not texto:
            return None

        texto_normalizado = (
            EntidadeContextualService
            ._normalizar_texto(
                texto
            )
        )

        tarefas = (
            EntidadeContextualService
            .listar_tarefas_unicas(
                db=db,
                id_usuario=id_usuario,
                id_conversa=id_conversa,
                limite=100
            )
        )

        # =====================================================
        # MATCH EXATO
        # =====================================================

        for entidade in tarefas:

            if not entidade.titulo:
                continue

            titulo = (
                EntidadeContextualService
                ._normalizar_texto(
                    entidade.titulo
                )
            )

            if titulo == texto_normalizado:
                return entidade


        # =====================================================
        # TÍTULO APARECE NA FRASE
        # =====================================================

        for entidade in tarefas:

            if not entidade.titulo:
                continue

            titulo = (
                EntidadeContextualService
                ._normalizar_texto(
                    entidade.titulo
                )
            )

            if (
                titulo
                and titulo in texto_normalizado
            ):
                return entidade


        # =====================================================
        # LIMPEZA DE EXPRESSÕES COMO:
        #
        # "a de java"
        # "a tarefa de python"
        # =====================================================

        texto_busca = texto_normalizado

        prefixos = [
            r"^a tarefa de\s+",
            r"^a tarefa\s+",
            r"^tarefa de\s+",
            r"^tarefa\s+",
            r"^a de\s+",
            r"^a do\s+",
            r"^a da\s+",
            r"^de\s+",
            r"^do\s+",
            r"^da\s+"
        ]

        for padrao in prefixos:

            texto_busca = re.sub(
                padrao,
                "",
                texto_busca
            )

        texto_busca = texto_busca.strip()

        if not texto_busca:
            return None


        for entidade in tarefas:

            if not entidade.titulo:
                continue

            titulo = (
                EntidadeContextualService
                ._normalizar_texto(
                    entidade.titulo
                )
            )

            if texto_busca in titulo:
                return entidade


        return None


    # =========================================================
    # RESOLVER POSIÇÃO
    # =========================================================

    @staticmethod
    def _resolver_posicao(
        texto: str
    ) -> int | None:

        texto = (
            EntidadeContextualService
            ._normalizar_texto(
                texto
            )
        )

        referencias = {

            1: [
                "a primeira",
                "primeira tarefa",
                "a primeira tarefa"
            ],

            2: [
                "a segunda",
                "segunda tarefa",
                "a segunda tarefa"
            ],

            3: [
                "a terceira",
                "terceira tarefa",
                "a terceira tarefa"
            ],

            4: [
                "a quarta",
                "quarta tarefa",
                "a quarta tarefa"
            ],

            5: [
                "a quinta",
                "quinta tarefa",
                "a quinta tarefa"
            ]
        }

        for posicao, termos in (
            referencias.items()
        ):

            for termo in termos:

                if (
                    EntidadeContextualService
                    ._contem_expressao(
                        texto,
                        termo
                    )
                ):

                    return posicao

        return None


    # =========================================================
    # RESOLVER REFERÊNCIA
    # =========================================================

    @staticmethod
    def resolver_referencia(
        db: Session,
        id_usuario: int,
        id_conversa: int,
        texto: str
    ) -> EntidadeContextual | None:

        if not texto:
            return None

        texto_normalizado = (
            EntidadeContextualService
            ._normalizar_texto(
                texto
            )
        )


        # =====================================================
        # 1. PRIMEIRA / SEGUNDA / TERCEIRA...
        # =====================================================

        posicao = (
            EntidadeContextualService
            ._resolver_posicao(
                texto_normalizado
            )
        )

        if posicao is not None:

            entidade = (
                EntidadeContextualService
                .obter_por_posicao(
                    db=db,
                    id_usuario=id_usuario,
                    id_conversa=id_conversa,
                    posicao=posicao
                )
            )

            if entidade is not None:
                return entidade


        # =====================================================
        # 2. FOCO ATUAL
        #
        # "ela"
        # "essa"
        # "essa tarefa"
        # "esta"
        # "a última"
        # =====================================================

        referencias_foco = [
            "ela",
            "essa",
            "essa tarefa",
            "esta",
            "esta tarefa",
            "a ultima",
            "ultima tarefa",
            "a ultima tarefa"
        ]

        for termo in referencias_foco:

            if (
                EntidadeContextualService
                ._contem_expressao(
                    texto_normalizado,
                    termo
                )
            ):

                return (
                    EntidadeContextualService
                    .obter_foco_atual(
                        db=db,
                        id_usuario=id_usuario,
                        id_conversa=id_conversa
                    )
                )


        # =====================================================
        # 3. FOCO ANTERIOR
        #
        # "anterior"
        # "a outra"
        # =====================================================

        referencias_anterior = [
            "a anterior",
            "tarefa anterior",
            "a tarefa anterior",
            "a outra",
            "outra tarefa",
            "a outra tarefa"
        ]

        for termo in referencias_anterior:

            if (
                EntidadeContextualService
                ._contem_expressao(
                    texto_normalizado,
                    termo
                )
            ):

                return (
                    EntidadeContextualService
                    .obter_foco_anterior(
                        db=db,
                        id_usuario=id_usuario,
                        id_conversa=id_conversa
                    )
                )


        # =====================================================
        # 4. BUSCA PELO TÍTULO
        # =====================================================

        return (
            EntidadeContextualService
            .buscar_por_titulo(
                db=db,
                id_usuario=id_usuario,
                id_conversa=id_conversa,
                texto=texto_normalizado
            )
        )

    @staticmethod
    def listar_entidades_unicas(
            db: Session,
            id_usuario: int,
            id_conversa: int,
            tipo_entidade: str,
            limite: int = 100
    ) -> list[EntidadeContextual]:

        entidades = (
            EntidadeContextualRepository
            .listar_recentes(
                db=db,
                id_usuario=id_usuario,
                id_conversa=id_conversa,
                tipo_entidade=tipo_entidade,
                limite=limite
            )
        )

        ids_encontrados = set()

        unicas = []

        for entidade in entidades:

            if entidade.id_entidade in ids_encontrados:
                continue

            ids_encontrados.add(
                entidade.id_entidade
            )

            unicas.append(
                entidade
            )

        return unicas

    @staticmethod
    def resolver_referencia_generica(
            db: Session,
            id_usuario: int,
            id_conversa: int,
            texto: str,
            tipo_entidade: str
    ) -> EntidadeContextual | None:

        texto = (
            EntidadeContextualService
            ._normalizar_texto(
                texto
            )
        )

        # =====================================================
        # FOCO ATUAL
        # =====================================================

        referencias_atual = [
            "ele",
            "ela",
            "esse",
            "essa",
            "este",
            "esta",
            "ultimo",
            "ultima",
            "ultimo lembrete",
            "ultima tarefa"
        ]

        for termo in referencias_atual:

            if (
                    EntidadeContextualService
                            ._contem_expressao(
                        texto,
                        termo
                    )
            ):
                return (
                    EntidadeContextualRepository
                    .buscar_foco_atual(
                        db=db,
                        id_usuario=id_usuario,
                        id_conversa=id_conversa,
                        tipo_entidade=tipo_entidade
                    )
                )

        # =====================================================
        # ANTERIOR
        # =====================================================

        referencias_anterior = [
            "anterior",
            "o anterior",
            "a anterior",
            "outro",
            "outra"
        ]

        for termo in referencias_anterior:

            if (
                    EntidadeContextualService
                            ._contem_expressao(
                        texto,
                        termo
                    )
            ):
                return (
                    EntidadeContextualRepository
                    .buscar_foco_anterior(
                        db=db,
                        id_usuario=id_usuario,
                        id_conversa=id_conversa,
                        tipo_entidade=tipo_entidade
                    )
                )

        return None