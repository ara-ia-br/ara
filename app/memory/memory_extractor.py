import json
import re
import unicodedata

from decimal import Decimal

from sqlalchemy.orm import Session

from app.ai.engine import (
    ai_engine
)


from app.memory.memory_consolidator import (
    MemoryConsolidator
)

class MemoryExtractor:

    # =========================================================
    # TIPOS PERMITIDOS
    # =========================================================

    TIPOS_PERMITIDOS = {
        "PREFERENCIA",
        "INTERESSE",
        "PESSOAL",
        "TRABALHO",
        "ESTUDO",
        "PROJETO",
        "ROTINA",
        "OBJETIVO",
        "CONFIGURACAO"
    }


    # =========================================================
    # IMPORTÂNCIA MÍNIMA PARA SALVAR
    # =========================================================

    IMPORTANCIA_MINIMA = Decimal(
        "35"
    )


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
    # DETECTAR PEDIDO PARA NÃO MEMORIZAR
    # =========================================================

    @staticmethod
    def _usuario_proibiu_memoria(
        mensagem: str
    ) -> bool:

        texto = (
            MemoryExtractor._normalizar(
                mensagem
            )
        )

        padroes = [
            r"\bnao guarde isso\b",
            r"\bnao memorize isso\b",
            r"\bnao lembra disso\b",
            r"\bnao lembre disso\b",
            r"\bnao salve isso\b",
            r"\bnao quero que voce guarde\b",
            r"\bnao quero que voce memorize\b",
            r"\bnao precisa guardar\b"
        ]

        return any(
            re.search(
                padrao,
                texto
            )
            for padrao in padroes
        )


    # =========================================================
    # DETECTAR COMANDO DE ESQUECIMENTO
    #
    # Nesta etapa NÃO exclui memória.
    # Apenas impede que a frase de esquecimento
    # vire uma nova memória.
    # =========================================================

    @staticmethod
    def _eh_comando_esquecimento(
        mensagem: str
    ) -> bool:

        texto = (
            MemoryExtractor._normalizar(
                mensagem
            )
        )

        gatilhos = [
            "esqueca",
            "esquece",
            "esquecer",
            "apague da memoria",
            "remova da memoria",
            "delete da memoria"
        ]

        return any(
            gatilho in texto
            for gatilho in gatilhos
        )


    # =========================================================
    # MENSAGENS ÓBVIAS QUE NÃO DEVEM VIRAR MEMÓRIA
    # =========================================================

    @staticmethod
    def _mensagem_irrelevante(
        mensagem: str
    ) -> bool:

        texto = (
            MemoryExtractor._normalizar(
                mensagem
            )
        )

        if not texto:
            return True


        # Muito curta para conter informação relevante.
        if len(texto) <= 3:
            return True


        mensagens_exatas = {
            "oi",
            "ola",
            "e ai",
            "blz",
            "beleza",
            "ok",
            "okay",
            "certo",
            "show",
            "valeu",
            "obrigado",
            "obrigada",
            "bom dia",
            "boa tarde",
            "boa noite",
            "entendi",
            "perfeito",
            "funcionou",
            "deu certo",
            "vamos",
            "vamos em frente",
            "vamos seguir",
            "avante"
        }

        if texto in mensagens_exatas:
            return True


        # =====================================================
        # PERGUNTAS GENÉRICAS
        # =====================================================

        perguntas_genericas = [
            r"^que horas sao[?]?$",
            r"^qual a hora[?]?$",
            r"^que dia e hoje[?]?$",
            r"^qual e a data[?]?$",
            r"^qual a data de hoje[?]?$",
            r"^como voce esta[?]?$",
            r"^tudo bem[?]?$"
        ]

        if any(
            re.search(
                padrao,
                texto
            )
            for padrao in perguntas_genericas
        ):
            return True


        # =====================================================
        # COMANDOS OPERACIONAIS
        #
        # Esses dados pertencem a tarefa/lembrete/contexto,
        # não à memória de longo prazo.
        # =====================================================

        comandos_operacionais = [
            "crie uma tarefa",
            "cria uma tarefa",
            "adicione uma tarefa",
            "adiciona uma tarefa",

            "conclua a tarefa",
            "conclui a tarefa",
            "cancele a tarefa",
            "cancela a tarefa",
            "inicie a tarefa",
            "inicia a tarefa",
            "reabra a tarefa",
            "reabre a tarefa",

            "crie um lembrete",
            "cria um lembrete",
            "me lembre",
            "me lembra",

            "cancele o lembrete",
            "cancela o lembrete",
            "conclua o lembrete",
            "conclui o lembrete",

            "liste minhas tarefas",
            "listar tarefas",
            "quais tarefas",
            "minhas tarefas",

            "listar lembretes",
            "meus lembretes",
            "quais lembretes"
        ]

        if any(
            comando in texto
            for comando in comandos_operacionais
        ):
            return True


        return False


    # =========================================================
    # DECIDIR SE VALE CHAMAR A IA
    # =========================================================

    @staticmethod
    def deve_analisar(
        mensagem: str
    ) -> bool:

        if not mensagem:
            return False

        if (
            MemoryExtractor
            ._usuario_proibiu_memoria(
                mensagem
            )
        ):
            return False

        if (
            MemoryExtractor
            ._eh_comando_esquecimento(
                mensagem
            )
        ):
            return False

        if (
            MemoryExtractor
            ._mensagem_irrelevante(
                mensagem
            )
        ):
            return False

        return True


    # =========================================================
    # EXTRAIR MEMÓRIAS
    # =========================================================

    @staticmethod
    def extrair(
        mensagem: str
    ) -> list[dict]:

        if not MemoryExtractor.deve_analisar(
            mensagem
        ):
            return []


        prompt = f"""
Você é o componente de extração de memória de longo prazo
do assistente pessoal JARVIS.

Analise SOMENTE a mensagem do usuário abaixo e identifique
informações pessoais ou contextuais que provavelmente continuarão
úteis em conversas futuras.

MENSAGEM DO USUÁRIO:

{mensagem}


=========================================================
O QUE PODE SER MEMORIZADO
=========================================================

Memorize somente informações como:

PREFERENCIA
- preferências de ferramentas;
- preferências de horários;
- preferências de resposta;
- preferências de trabalho ou estudo.

INTERESSE
- assuntos de interesse recorrente;
- tecnologias;
- áreas de estudo;
- hobbies relevantes.

PESSOAL
- informações pessoais úteis e persistentes
  fornecidas explicitamente pelo usuário.

TRABALHO
- profissão;
- área profissional;
- tecnologias usadas no trabalho;
- contexto profissional persistente.

ESTUDO
- curso;
- área de estudo;
- matérias importantes;
- tecnologias que está aprendendo.

PROJETO
- projetos relevantes em desenvolvimento;
- tecnologias utilizadas;
- finalidade de um projeto.

ROTINA
- hábitos recorrentes;
- horários habituais;
- rotina de trabalho ou estudo.

OBJETIVO
- metas profissionais;
- metas acadêmicas;
- objetivos de aprendizado;
- objetivos pessoais relevantes.

CONFIGURACAO
- preferências persistentes sobre como o JARVIS
  deve se comportar ou responder.


=========================================================
NÃO MEMORIZE
=========================================================

NÃO salve:

- cumprimentos;
- agradecimentos;
- perguntas comuns;
- comandos para tarefas;
- comandos para lembretes;
- ações operacionais;
- datas usadas apenas em uma tarefa;
- informações claramente momentâneas;
- respostas do próprio assistente;
- frases sem informação útil;
- informações inferidas sem terem sido afirmadas;
- hipóteses;
- informações que o usuário não afirmou;
- dados temporários sem utilidade futura.


=========================================================
CONTEÚDO DA MEMÓRIA
=========================================================

O campo "conteudo" deve ser:

- curto;
- objetivo;
- escrito em terceira pessoa;
- autossuficiente;
- sem mencionar "a mensagem";
- sem mencionar banco de dados;
- sem mencionar memória interna;
- sem inventar detalhes.

Exemplo correto:

"Usuário prefere estudar à noite."

Exemplo incorreto:

"Na mensagem atual, o usuário disse que talvez goste
de estudar à noite."


=========================================================
IMPORTÂNCIA
=========================================================

A importância deve ser um número entre 0 e 100.

Use aproximadamente:

90-100:
informação central para o usuário ou objetivo importante.

70-89:
preferência, rotina, projeto ou contexto muito útil.

50-69:
informação útil, mas secundária.

35-49:
informação com alguma utilidade futura.

Abaixo de 35:
não deve ser retornada.


=========================================================
TIPOS PERMITIDOS
=========================================================

PREFERENCIA
INTERESSE
PESSOAL
TRABALHO
ESTUDO
PROJETO
ROTINA
OBJETIVO
CONFIGURACAO


=========================================================
FORMATO DA RESPOSTA
=========================================================

Responda SOMENTE com JSON válido.

Não use markdown.

Não use ```json.

Formato:

{{
    "memorias": [
        {{
            "tipo": "PREFERENCIA",
            "conteudo": "Usuário prefere estudar à noite.",
            "importancia": 80
        }}
    ]
}}

Caso não exista memória relevante:

{{
    "memorias": []
}}
"""


        resposta = (
            ai_engine.gerar_resposta(
                [
                    {
                        "role": "system",
                        "content": (
                            "Você é um extrator estruturado "
                            "de memória de longo prazo. "
                            "Retorne exclusivamente JSON válido. "
                            "Nunca invente informações."
                        )
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
        )


        return (
            MemoryExtractor._interpretar_json(
                resposta
            )
        )


    # =========================================================
    # INTERPRETAR JSON
    # =========================================================

    @staticmethod
    def _interpretar_json(
        resposta: str
    ) -> list[dict]:

        if not resposta:
            return []


        # =====================================================
        # REMOVE MARKDOWN DE MODELOS LOCAIS
        # =====================================================

        resposta_limpa = re.sub(
            r"```(?:json)?",
            "",
            resposta,
            flags=re.IGNORECASE
        )

        resposta_limpa = (
            resposta_limpa
            .replace(
                "```",
                ""
            )
            .strip()
        )


        # =====================================================
        # TENTA RECUPERAR APENAS O JSON
        # =====================================================

        match = re.search(
            r"\{.*\}",
            resposta_limpa,
            flags=re.DOTALL
        )

        if match:

            resposta_limpa = (
                match.group(0)
            )


        try:

            dados = json.loads(
                resposta_limpa
            )

        except (
            json.JSONDecodeError,
            TypeError
        ):

            print(
                "MemoryExtractor: "
                "modelo retornou JSON inválido."
            )

            return []


        if not isinstance(
            dados,
            dict
        ):
            return []


        memorias = dados.get(
            "memorias",
            []
        )


        if not isinstance(
            memorias,
            list
        ):
            return []


        resultado = []


        for memoria in memorias:

            if not isinstance(
                memoria,
                dict
            ):
                continue


            tipo = str(
                memoria.get(
                    "tipo",
                    ""
                )
            ).upper().strip()


            conteudo = str(
                memoria.get(
                    "conteudo",
                    ""
                )
            ).strip()


            try:

                importancia = Decimal(
                    str(
                        memoria.get(
                            "importancia",
                            50
                        )
                    )
                )

            except Exception:

                importancia = (
                    Decimal("50")
                )


            # =================================================
            # VALIDA TIPO
            # =================================================

            if (
                tipo
                not in
                MemoryExtractor.TIPOS_PERMITIDOS
            ):
                continue


            # =================================================
            # VALIDA CONTEÚDO
            # =================================================

            if not conteudo:
                continue


            if len(conteudo) < 5:
                continue


            # Evita memórias absurdamente longas.
            if len(conteudo) > 500:

                conteudo = (
                    conteudo[:500]
                    .strip()
                )


            # =================================================
            # LIMITA IMPORTÂNCIA
            # =================================================

            importancia = max(
                Decimal("0"),
                min(
                    Decimal("100"),
                    importancia
                )
            )


            # =================================================
            # DESCARTA MEMÓRIA DE BAIXA IMPORTÂNCIA
            # =================================================

            if (
                importancia
                <
                MemoryExtractor.IMPORTANCIA_MINIMA
            ):
                continue


            resultado.append(
                {
                    "tipo": tipo,
                    "conteudo": conteudo,
                    "importancia": importancia
                }
            )


        # =====================================================
        # REMOVE DUPLICATAS DA MESMA EXTRAÇÃO
        # =====================================================

        resultado_unico = []

        conteudos_encontrados = set()


        for memoria in resultado:

            conteudo_normalizado = (
                MemoryExtractor._normalizar(
                    memoria["conteudo"]
                )
            )


            if (
                conteudo_normalizado
                in conteudos_encontrados
            ):
                continue


            conteudos_encontrados.add(
                conteudo_normalizado
            )

            resultado_unico.append(
                memoria
            )


        return resultado_unico

    # =========================================================
    # PROCESSAR E SALVAR
    # =========================================================

    # =========================================================
    # PROCESSAR MEMÓRIAS
    # =========================================================

    @staticmethod
    def processar(
        db: Session,
        id_usuario: int,
        mensagem: str
    ) -> list:

        if id_usuario is None:
            return []

        if not MemoryExtractor.deve_analisar(
            mensagem
        ):
            return []

        # =====================================================
        # EXTRAÇÃO
        # =====================================================

        memorias_extraidas = (
            MemoryExtractor.extrair(
                mensagem
            )
        )

        if not memorias_extraidas:
            return []

        memorias_processadas = []

        # =====================================================
        # CONSOLIDAÇÃO
        # =====================================================

        for dados in memorias_extraidas:

            resultado = (
                MemoryConsolidator.consolidar(
                    db=db,
                    id_usuario=id_usuario,
                    tipo=dados["tipo"],
                    conteudo=dados["conteudo"],
                    importancia=dados["importancia"]
                )
            )

            if resultado.memoria is not None:
                memorias_processadas.append(
                    resultado.memoria
                )

        return memorias_processadas