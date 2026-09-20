import re
import unicodedata

from sqlalchemy.orm import Session

from app.models.memoria import (
    Memoria
)

from app.repositories.memoria_repository import (
    MemoriaRepository
)


class MemoryManager:

    # =========================================================
    # STOPWORDS
    #
    # Palavras muito comuns que não ajudam a determinar
    # relevância semântica.
    # =========================================================

    STOPWORDS = {
        "a",
        "o",
        "as",
        "os",
        "um",
        "uma",
        "uns",
        "umas",

        "de",
        "da",
        "do",
        "das",
        "dos",

        "em",
        "no",
        "na",
        "nos",
        "nas",

        "para",
        "pra",
        "por",
        "com",
        "sem",

        "e",
        "ou",
        "mas",
        "que",

        "eu",
        "me",
        "meu",
        "minha",
        "meus",
        "minhas",

        "voce",
        "voces",

        "ele",
        "ela",
        "eles",
        "elas",

        "isso",
        "isto",
        "aquilo",

        "esse",
        "essa",
        "este",
        "esta",

        "ser",
        "estar",
        "ter",
        "fazer",

        "sou",
        "estou",
        "tenho",

        "é",
        "e",

        "muito",
        "mais",
        "menos",

        "agora",
        "hoje",

        "sobre",
        "como",

        "quero",
        "queria",
        "gostaria",

        "pode",
        "poderia"
    }


    # =========================================================
    # PESOS POR TIPO
    #
    # Algumas memórias possuem maior chance de serem úteis
    # em decisões futuras.
    # =========================================================

    PESO_TIPO = {
        "OBJETIVO": 12,
        "PREFERENCIA": 10,
        "CONFIGURACAO": 10,
        "PROJETO": 9,
        "TRABALHO": 8,
        "ESTUDO": 8,
        "ROTINA": 7,
        "INTERESSE": 5,
        "PESSOAL": 4
    }


    # =========================================================
    # NORMALIZAR TEXTO
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
            if unicodedata.category(
                caractere
            ) != "Mn"
        )

        texto = re.sub(
            r"\s+",
            " ",
            texto
        )

        return texto.strip()


    # =========================================================
    # EXTRAIR PALAVRAS RELEVANTES
    # =========================================================

    @staticmethod
    def _palavras(
        texto: str
    ) -> set[str]:

        texto = (
            MemoryManager._normalizar(
                texto
            )
        )

        palavras = set(
            re.findall(
                r"\b[a-z0-9]+\b",
                texto
            )
        )

        palavras = {
            palavra
            for palavra in palavras
            if (
                palavra
                not in MemoryManager.STOPWORDS
                and len(palavra) >= 3
            )
        }

        return palavras


    # =========================================================
    # DETECTAR TERMOS IMPORTANTES
    #
    # Palavras técnicas ou específicas recebem um peso maior.
    # =========================================================

    @staticmethod
    def _termos_importantes(
        texto: str
    ) -> set[str]:

        palavras = (
            MemoryManager._palavras(
                texto
            )
        )

        importantes = set()

        for palavra in palavras:

            # Nomes de tecnologias, siglas ou termos
            # específicos tendem a ter maior valor.
            if len(palavra) >= 5:
                importantes.add(
                    palavra
                )

        return importantes


    # =========================================================
    # SIMILARIDADE SIMPLES ENTRE CONJUNTOS
    # =========================================================

    @staticmethod
    def _similaridade(
        palavras_a: set[str],
        palavras_b: set[str]
    ) -> float:

        if (
            not palavras_a
            or not palavras_b
        ):
            return 0.0

        intersecao = (
            palavras_a
            &
            palavras_b
        )

        uniao = (
            palavras_a
            |
            palavras_b
        )

        if not uniao:
            return 0.0

        return (
            len(intersecao)
            /
            len(uniao)
        )


    # =========================================================
    # DETECTAR SE A MENSAGEM É GENÉRICA
    #
    # Evita injetar memória sem necessidade.
    # =========================================================

    @staticmethod
    def _mensagem_generica(
        mensagem: str
    ) -> bool:

        texto = (
            MemoryManager._normalizar(
                mensagem
            )
        )

        genericas = {
            "oi",
            "ola",
            "blz",
            "beleza",
            "obrigado",
            "obrigada",
            "valeu",
            "ok",
            "certo",
            "perfeito",
            "bom dia",
            "boa tarde",
            "boa noite"
        }

        if texto in genericas:
            return True

        if len(texto) <= 3:
            return True

        return False


    # =========================================================
    # DETECTAR INTENÇÕES DE MEMÓRIA
    #
    # Permite recuperar memórias mesmo quando a pergunta
    # não compartilha palavras literais com o conteúdo salvo.
    #
    # Exemplo:
    # "qual é meu nome?" -> PESSOAL
    # "qual minha linguagem favorita?" -> PREFERENCIA
    # =========================================================

    @staticmethod
    def _detectar_intencoes_memoria(
        mensagem: str
    ) -> set[str]:

        texto = MemoryManager._normalizar(
            mensagem
        )

        intencoes = set()

        # -------------------------------------------------
        # INFORMAÇÕES PESSOAIS
        # -------------------------------------------------

        termos_pessoais = (
            "meu nome",
            "qual meu nome",
            "qual e meu nome",
            "qual e o meu nome",
            "como eu me chamo",
            "quem sou eu",
            "sobre mim"
        )

        if any(
            termo in texto
            for termo in termos_pessoais
        ):
            intencoes.add("PESSOAL")

        # -------------------------------------------------
        # PREFERÊNCIAS
        # -------------------------------------------------

        termos_preferencia = (
            "minha preferencia",
            "minhas preferencias",
            "eu prefiro",
            "que eu prefiro",
            "preferida",
            "preferido",
            "favorita",
            "favorito",
            "gosto mais",
            "qual linguagem eu gosto",
            "linguagem de programacao favorita",
            "linguagem de programacao preferida"
        )

        if any(
            termo in texto
            for termo in termos_preferencia
        ):
            intencoes.add("PREFERENCIA")

        # -------------------------------------------------
        # OBJETIVOS
        # -------------------------------------------------

        termos_objetivo = (
            "meu objetivo",
            "meus objetivos",
            "minha meta",
            "minhas metas",
            "quero alcancar",
            "quero conseguir"
        )

        if any(
            termo in texto
            for termo in termos_objetivo
        ):
            intencoes.add("OBJETIVO")

        # -------------------------------------------------
        # TRABALHO
        # -------------------------------------------------

        termos_trabalho = (
            "meu trabalho",
            "onde eu trabalho",
            "com o que eu trabalho",
            "minha profissao",
            "meu emprego"
        )

        if any(
            termo in texto
            for termo in termos_trabalho
        ):
            intencoes.add("TRABALHO")

        # -------------------------------------------------
        # ESTUDO
        # -------------------------------------------------

        termos_estudo = (
            "o que eu estudo",
            "oque eu estudo",
            "onde eu estudo",
            "minha faculdade",
            "meu curso",
            "meus estudos"
        )

        if any(
            termo in texto
            for termo in termos_estudo
        ):
            intencoes.add("ESTUDO")

        # -------------------------------------------------
        # PROJETOS
        # -------------------------------------------------

        termos_projeto = (
            "meu projeto",
            "meus projetos",
            "projeto que estou fazendo",
            "projeto que eu estou fazendo",
            "projeto que estou desenvolvendo",
            "projeto que eu estou desenvolvendo"
        )

        if any(
            termo in texto
            for termo in termos_projeto
        ):
            intencoes.add("PROJETO")

        return intencoes


    # =========================================================
    # CALCULAR PONTUAÇÃO DE MEMÓRIA
    # =========================================================

    @staticmethod
    def _pontuar_memoria(
        memoria: Memoria,
        mensagem_atual: str
    ) -> float:

        palavras_mensagem = (
            MemoryManager._palavras(
                mensagem_atual
            )
        )

        palavras_memoria = (
            MemoryManager._palavras(
                memoria.conteudo
            )
        )


        # =====================================================
        # 1. CORRESPONDÊNCIA DIRETA
        # =====================================================

        correspondencias = (
            palavras_mensagem
            &
            palavras_memoria
        )

        pontos_correspondencia = (
            len(correspondencias)
            * 18
        )


        # =====================================================
        # 2. SIMILARIDADE
        # =====================================================

        similaridade = (
            MemoryManager._similaridade(
                palavras_mensagem,
                palavras_memoria
            )
        )

        pontos_similaridade = (
            similaridade
            * 35
        )


        # =====================================================
        # 3. TERMOS IMPORTANTES
        # =====================================================

        termos_mensagem = (
            MemoryManager
            ._termos_importantes(
                mensagem_atual
            )
        )

        termos_memoria = (
            MemoryManager
            ._termos_importantes(
                memoria.conteudo
            )
        )

        termos_comuns = (
            termos_mensagem
            &
            termos_memoria
        )

        pontos_termos = (
            len(termos_comuns)
            * 10
        )


        # =====================================================
        # 4. IMPORTÂNCIA DA MEMÓRIA
        # =====================================================

        importancia = float(
            memoria.importancia
            or 0
        )

        # Reduz o peso para não deixar importância
        # dominar completamente a relevância.
        pontos_importancia = (
            importancia
            * 0.25
        )


        # =====================================================
        # 5. TIPO DA MEMÓRIA
        # =====================================================

        tipo = str(
            memoria.tipo_memoria
            or ""
        ).upper()

        pontos_tipo = (
            MemoryManager
            .PESO_TIPO
            .get(
                tipo,
                0
            )
        )


        # =====================================================
        # PONTUAÇÃO FINAL
        # =====================================================

        pontuacao = (
            pontos_correspondencia
            +
            pontos_similaridade
            +
            pontos_termos
            +
            pontos_importancia
            +
            pontos_tipo
        )

        return pontuacao


    # =========================================================
    # BUSCAR MEMÓRIAS RELEVANTES
    # =========================================================

    @staticmethod
    def buscar_relevantes(
        db: Session,
        id_usuario: int,
        mensagem_atual: str,
        limite: int = 5
    ) -> list[Memoria]:

        if id_usuario is None:
            return []

        if not mensagem_atual:
            return []

        if limite <= 0:
            return []


        # =====================================================
        # NÃO BUSCA MEMÓRIA PARA MENSAGENS GENÉRICAS
        # =====================================================

        if (
            MemoryManager
            ._mensagem_generica(
                mensagem_atual
            )
        ):
            return []


        memorias = (
            MemoriaRepository
            .listar_ativas_usuario(
                db,
                id_usuario
            )
        )


        if not memorias:
            return []


        pontuadas = []


        for memoria in memorias:

            if not memoria.conteudo:
                continue


            pontuacao = (
                MemoryManager
                ._pontuar_memoria(
                    memoria,
                    mensagem_atual
                )
            )


            # =================================================
            # LIMIAR MÍNIMO
            #
            # Impede memória sem relação de entrar apenas
            # porque possui importância alta.
            # =================================================

            palavras_mensagem = (
                MemoryManager._palavras(
                    mensagem_atual
                )
            )

            palavras_memoria = (
                MemoryManager._palavras(
                    memoria.conteudo
                )
            )

            correspondencias = (
                palavras_mensagem
                &
                palavras_memoria
            )


            # =================================================
            # RELEVÂNCIA POR INTENÇÃO
            #
            # Uma memória pode ser relevante semanticamente
            # mesmo sem compartilhar palavras literais.
            #
            # Exemplo:
            # "qual é meu nome?"
            # memória: "Usuário se chama Brayan."
            # =================================================

            intencoes = (
                MemoryManager
                ._detectar_intencoes_memoria(
                    mensagem_atual
                )
            )

            tipo_memoria = str(
                memoria.tipo_memoria
                or ""
            ).upper()

            relevante_por_intencao = (
                tipo_memoria
                in intencoes
            )

            # Sem correspondência lexical E sem intenção
            # compatível, a memória continua sendo descartada.
            if (
                not correspondencias
                and not relevante_por_intencao
            ):
                continue

            # Intenção explícita recebe peso forte.
            if relevante_por_intencao:
                pontuacao += 40

            if pontuacao < 20:
                continue


            pontuadas.append(
                (
                    pontuacao,
                    memoria
                )
            )


        pontuadas.sort(
            key=lambda item: item[0],
            reverse=True
        )


        return [
            memoria
            for _, memoria
            in pontuadas[:limite]
        ]


    # =========================================================
    # MONTAR CONTEXTO PARA IA
    # =========================================================

    @staticmethod
    def montar_contexto(
        memorias: list[Memoria]
    ) -> str:

        if not memorias:
            return ""


        linhas = [
            (
                "Informações persistentes e relevantes "
                "sobre o usuário:"
            ),
            (
                "Use estas informações somente quando "
                "forem úteis para responder à mensagem atual."
            ),
            (
                "Não mencione que estas informações "
                "vieram de memória interna."
            ),
            ""
        ]


        for memoria in memorias:

            tipo = str(
                memoria.tipo_memoria
                or "CONTEXTO"
            ).upper()

            conteudo = (
                memoria.conteudo
                or ""
            ).strip()

            if not conteudo:
                continue


            linhas.append(
                f"- [{tipo}] {conteudo}"
            )


        return "\n".join(
            linhas
        )