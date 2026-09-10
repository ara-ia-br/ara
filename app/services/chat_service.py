from time import perf_counter

import re

from sqlalchemy.orm import Session

from app.security.settings import setting


from app.services.time_service import (
    TimeService
)

from app.services.entidade_contextual_service import (
    EntidadeContextualService
)

from app.services.contexto_agente_service import (
    ContextoAgenteService
)

from app.ai.engine import ai_engine

from app.agent.agent import JarvisAgent
from app.agent.intent import TipoAcao
from app.agent.tool_registry import ToolRegistry

from app.memory.memory_extractor import MemoryExtractor
from app.memory.memory_manager import MemoryManager

from app.models.mensagem import (
    Mensagem,
    RemetenteMensagem
)

from app.repositories.conversa_repository import (
    ConversaRepository
)

from app.repositories.mensagem_repository import (
    MensagemRepository
)

from app.services.conversa_service import (
    ConversaService
)


class ChatService:

    # =========================================================
    # SALVAR INTERAÇÃO DO AGENT
    # =========================================================

    @staticmethod
    def _salvar_interacao_agent(
        db: Session,
        id_conversa: int,
        conteudo_usuario: str,
        resposta_jarvis: str
    ) -> None:

        mensagem_usuario = Mensagem(
            id_conversa=id_conversa,
            remetente=RemetenteMensagem.USUARIO,
            conteudo=conteudo_usuario,
            tipo="TEXTO"
        )

        MensagemRepository.criar(
            db,
            mensagem_usuario
        )

        mensagem_jarvis = Mensagem(
            id_conversa=id_conversa,
            remetente=RemetenteMensagem.JARVIS,
            conteudo=resposta_jarvis,
            tipo="TEXTO",
            modelo_ia="AGENT",
            tempo_processamento=0
        )

        MensagemRepository.criar(
            db,
            mensagem_jarvis
        )

        ConversaService.atualizar_atividade(
            db,
            id_conversa
        )


    # =========================================================
    # EXTRAÇÃO DE MEMÓRIA
    # =========================================================

    @staticmethod
    def _extrair_memoria(
            db: Session,
            id_usuario: int,
            conteudo: str
    ) -> None:

        try:

            inicio_extracao = perf_counter()

            MemoryExtractor.processar(
                db=db,
                id_usuario=id_usuario,
                mensagem=conteudo
            )

            print(
                f"[PERFORMANCE] Extração memória: "
                f"{perf_counter() - inicio_extracao:.2f}s"
            )

        except Exception as erro:

            print(
                f"Erro ao extrair memória: {erro}"
            )

    # =========================================================
    # LIMPAR TÍTULOS DO AGENT
    # =========================================================

    @staticmethod
    def _limpar_titulo(
        texto: str
    ) -> str:

        texto = re.sub(
            r"\bprioridade\s+(máxima|maxima|alta|baixa|muito baixa|[1-5])\b",
            "",
            texto,
            flags=re.IGNORECASE
        )

        texto = re.sub(
            r"\b(urgente|urgentemente|muito urgente)\b",
            "",
            texto,
            flags=re.IGNORECASE
        )

        texto = re.sub(
            r"\s+",
            " ",
            texto
        )

        texto = texto.strip(
            " ,.-"
        )

        texto = re.sub(
            r"^para\s+",
            "",
            texto,
            flags=re.IGNORECASE
        )

        if not texto:
            return texto

        texto = texto.strip()

        texto = re.sub(
            r"""
            [,\s]*
            (
                por\s+favor
                |
                por\s+gentileza
                |
                pfv
                |
                pra\s+mim
                |
                para\s+mim
                |
                obrigado
                |
                obrigada
                |
                obg
                |
                beleza
                |
                blz
            )
            [.!?]*$
            """,
            "",
            texto,
            flags=(
                re.IGNORECASE
                | re.VERBOSE
            )
        )

        texto = texto.strip(
            " ,.!?;:-"
        )

        return texto


    # =========================================================
    # FORMATAR RESPOSTA DAS TOOLS
    # =========================================================

    @staticmethod
    def _formatar_resposta_tool(
        ferramenta: str,
        resultado: dict
    ) -> str:

        if ferramenta == "listar_tarefas_periodo":

            tarefas = resultado.get(
                "tarefas",
                []
            )

            if not tarefas:
                return (
                    "Você não tem nenhuma tarefa "
                    "nesse período."
                )

            linhas = [
                "Suas tarefas nesse período:"
            ]

            for tarefa in tarefas:
                data_limite = tarefa.get(
                    "data_limite"
                )

                linhas.append(
                    f"- {tarefa['titulo']} "
                    f"({tarefa['status']})"
                    + (
                        f" — {data_limite}"
                        if data_limite
                        else ""
                    )
                )

            return "\n".join(
                linhas
            )



        # =====================================================
        # LEMBRETES
        # =====================================================

        if ferramenta == "criar_lembrete":

            return (
                f"Fechou! Lembrete criado: "
                f"{resultado['titulo']} "
                f"para {resultado['data_hora']}."
            )


        if ferramenta == "listar_lembretes":

            lembretes = resultado.get(
                "lembretes",
                []
            )

            if not lembretes:

                return (
                    "Você não tem nenhum lembrete "
                    "pendente no momento."
                )

            linhas = [
                "Seus lembretes pendentes:"
            ]

            for lembrete in lembretes:

                data_hora = lembrete.get(
                    "data_hora"
                )

                if data_hora:

                    linhas.append(
                        f"- {lembrete['titulo']} — "
                        f"{data_hora}"
                    )

                else:

                    linhas.append(
                        f"- {lembrete['titulo']}"
                    )

            return "\n".join(
                linhas
            )


        if ferramenta == "cancelar_lembrete":

            return (
                f"Fechou! Cancelei o lembrete "
                f"'{resultado['titulo']}'."
            )


        if ferramenta == "concluir_lembrete":

            return (
                f"Boa! Marquei o lembrete "
                f"'{resultado['titulo']}' "
                f"como concluído."
            )


        # =====================================================
        # TAREFAS
        # =====================================================

        if ferramenta == "criar_tarefa":

            return (
                f"Fechou! Criei a tarefa "
                f"'{resultado['titulo']}'."
            )

        if ferramenta == "editar_tarefa":
            return (
                f"Fechou! Atualizei a tarefa "
                f"'{resultado['titulo']}'."
            )


        if ferramenta == "listar_tarefas":

            tarefas = resultado.get(
                "tarefas",
                []
            )

            if not tarefas:

                return (
                    "Você ainda não tem nenhuma tarefa."
                )

            linhas = [
                "Suas tarefas:"
            ]

            for tarefa in tarefas:

                linhas.append(
                    f"- {tarefa['titulo']} "
                    f"({tarefa['status']})"
                )

            return "\n".join(
                linhas
            )


        if ferramenta == "iniciar_tarefa":

            return (
                f"Boa! A tarefa "
                f"'{resultado['titulo']}' "
                f"agora está em andamento."
            )


        if ferramenta == "concluir_tarefa":

            return (
                f"Boa! Marquei a tarefa "
                f"'{resultado['titulo']}' "
                f"como concluída."
            )


        if ferramenta == "cancelar_tarefa":

            return (
                f"Fechou! Cancelei a tarefa "
                f"'{resultado['titulo']}'."
            )


        if ferramenta == "reabrir_tarefa":

            return (
                f"Fechou! Reabri a tarefa "
                f"'{resultado['titulo']}'. "
                f"Ela voltou para pendente."
            )


        # =====================================================
        #FALLBACK
        # =====================================================

        return (
            "A ação foi executada com sucesso."
        )


    # =========================================================
    # MÉTODO PRINCIPAL
    # =========================================================

    @staticmethod
    def enviar_mensagem(
        db: Session,
        id_conversa: int,
        conteudo: str
    ) -> dict:

        # =====================================================
        # 1. BUSCA A CONVERSA
        # =====================================================

        conversa = ConversaRepository.buscar_por_id(
            db,
            id_conversa
        )

        if conversa is None:

            raise ValueError(
                "Conversa não encontrada."
            )


        # =====================================================
        # 2. IDENTIFICA O USUÁRIO
        # =====================================================

        id_usuario = conversa.id_usuario


        # =====================================================
        # 3. GERA TÍTULO AUTOMÁTICO DA CONVERSA
        # =====================================================

        ConversaService.gerar_titulo_automatico(
            db=db,
            id_conversa=id_conversa,
            primeira_mensagem=conteudo
        )

        inicio_agent = perf_counter()

        decisao = JarvisAgent.decidir(
            mensagem=conteudo,
            db=db,
            id_usuario=id_usuario,
            id_conversa=id_conversa
        )

        print(
            f"[PERFORMANCE] Agent: "
            f"{perf_counter() - inicio_agent:.2f}s"
        )




        # =====================================================
        # 4. AGENT
        # =====================================================

        # =====================================================
        # 5. EXECUTAR TOOL
        # =====================================================

        if decisao.acao == TipoAcao.EXECUTAR:

            argumentos = (
                decisao.argumentos.copy()
                if decisao.argumentos
                else {}
            )


            # O backend injeta esses dados.
            # Nunca devem depender da IA.
            argumentos["db"] = db
            argumentos["id_usuario"] = id_usuario


            try:

                # =================================================
                # LIMPA TÍTULO
                # =================================================

                if "titulo" in argumentos:

                    argumentos["titulo"] = (
                        ChatService._limpar_titulo(
                            argumentos["titulo"]
                        )
                    )


                # =================================================
                # EXECUTA TOOL
                # =================================================

                resultado = ToolRegistry.executar(
                    decisao.ferramenta,
                    **argumentos
                )

                # =====================================================
                # ATUALIZA CONTEXTO OPERACIONAL DE TAREFA
                # =====================================================

                if (
                        isinstance(resultado, dict)
                        and resultado.get("id_tarefa") is not None
                        and "tarefa" in str(decisao.ferramenta)
                ):
                    id_tarefa_resultado = resultado.get(
                        "id_tarefa"
                    )

                    titulo_tarefa_resultado = resultado.get(
                        "titulo"
                    )

                    print(
                        "\n===== CONTEXTO DEBUG ====="
                    )

                    print(
                        "Ferramenta:",
                        decisao.ferramenta
                    )

                    print(
                        "Usuário:",
                        id_usuario
                    )

                    print(
                        "Conversa:",
                        id_conversa
                    )

                    print(
                        "ID tarefa:",
                        id_tarefa_resultado
                    )

                    print(
                        "Título:",
                        titulo_tarefa_resultado
                    )

                    print(
                        "==========================\n"
                    )

                    ContextoAgenteService.registrar_tarefa(
                        db=db,
                        id_usuario=id_usuario,
                        id_conversa=id_conversa,
                        id_tarefa=id_tarefa_resultado,
                        ferramenta=decisao.ferramenta
                    )

                    EntidadeContextualService.registrar(
                        db=db,
                        id_usuario=id_usuario,
                        id_conversa=id_conversa,
                        tipo_entidade="TAREFA",
                        id_entidade=id_tarefa_resultado,
                        titulo=titulo_tarefa_resultado
                    )



                # =====================================================
                # REGISTRA LEMBRETE NO CONTEXTO
                # =====================================================

                if (
                        isinstance(resultado, dict)
                        and resultado.get("id_lembrete") is not None
                        and "lembrete" in str(decisao.ferramenta)
                ):
                    EntidadeContextualService.registrar(
                        db=db,
                        id_usuario=id_usuario,
                        id_conversa=id_conversa,
                        tipo_entidade="LEMBRETE",
                        id_entidade=resultado["id_lembrete"],
                        titulo=resultado.get("titulo")
                    )

                # =====================================================
                # ATUALIZA CONTEXTO OPERACIONAL
                # =====================================================




            # =====================================================
            # ERRO FUNCIONAL
            # =====================================================

            except ValueError as erro:

                resposta = str(
                    erro
                )

                ChatService._salvar_interacao_agent(
                    db=db,
                    id_conversa=id_conversa,
                    conteudo_usuario=conteudo,
                    resposta_jarvis=resposta
                )

                #ChatService._extrair_memoria(
                #    db=db,
               #     id_usuario=id_usuario,
                #    conteudo=conteudo
               # )

                return {
                    "id_conversa": id_conversa,
                    "mensagem_usuario": conteudo,
                    "resposta_jarvis": resposta,
                    "modelo": "AGENT",
                    "ferramenta": decisao.ferramenta,
                    "tempo_processamento": 0
                }


            # =====================================================
            # ARGUMENTO OBRIGATÓRIO AUSENTE
            # =====================================================

            except TypeError as erro:

                print(
                    f"Erro de argumentos da ferramenta "
                    f"'{decisao.ferramenta}': {erro}"
                )


                if (
                    "tarefa"
                    in str(decisao.ferramenta)
                ):

                    resposta = (
                        "Preciso saber qual tarefa você "
                        "quer alterar. Me diga o nome dela."
                    )

                elif (
                    "lembrete"
                    in str(decisao.ferramenta)
                ):

                    resposta = (
                        "Preciso saber qual lembrete você "
                        "quer alterar. Me diga qual é."
                    )

                else:

                    resposta = (
                        "Faltou uma informação para eu "
                        "executar essa ação. "
                        "Pode especificar melhor?"
                    )


                ChatService._salvar_interacao_agent(
                    db=db,
                    id_conversa=id_conversa,
                    conteudo_usuario=conteudo,
                    resposta_jarvis=resposta
                )

                return {
                    "id_conversa": id_conversa,
                    "mensagem_usuario": conteudo,
                    "resposta_jarvis": resposta,
                    "modelo": "AGENT",
                    "ferramenta": decisao.ferramenta,
                    "tempo_processamento": 0
                }


            # =====================================================
            # 6. FORMATA RESPOSTA DA TOOL
            # =====================================================

            resposta = (
                ChatService._formatar_resposta_tool(
                    decisao.ferramenta,
                    resultado
                )
            )


            # =====================================================
            # 7. SALVA A INTERAÇÃO
            # =====================================================

            ChatService._salvar_interacao_agent(
                db=db,
                id_conversa=id_conversa,
                conteudo_usuario=conteudo,
                resposta_jarvis=resposta
            )


            # =====================================================
            # 8. MEMÓRIA
            # =====================================================

            #ChatService._extrair_memoria(
             #   db=db,
              #  id_usuario=id_usuario,
               # conteudo=conteudo
            #)


            # =====================================================
            # 9. RETORNO DO AGENT
            # =====================================================

            return {
                "id_conversa": id_conversa,
                "mensagem_usuario": conteudo,
                "resposta_jarvis": resposta,
                "modelo": "AGENT",
                "ferramenta": decisao.ferramenta,
                "tempo_processamento": 0
            }

        inicio_memoria = perf_counter()

        memorias = MemoryManager.buscar_relevantes(
            db=db,
            id_usuario=id_usuario,
            mensagem_atual=conteudo,
            limite=5
        )

        print(
            f"[PERFORMANCE] Busca memória: "
            f"{perf_counter() - inicio_memoria:.2f}s"
        )


        # =========================================================
        # 10. FLUXO NORMAL DE CONVERSA
        # =========================================================



        contexto_memoria = (
            MemoryManager.montar_contexto(
                memorias
            )
        )


        # =========================================================
        # 11. SALVA MENSAGEM DO USUÁRIO
        # =========================================================

        mensagem_usuario = Mensagem(
            id_conversa=id_conversa,
            remetente=RemetenteMensagem.USUARIO,
            conteudo=conteudo,
            tipo="TEXTO"
        )

        MensagemRepository.criar(
            db,
            mensagem_usuario
        )


        # =========================================================
        # 12. BUSCA HISTÓRICO
        # =========================================================

        historico = (
            MensagemRepository.listar_por_conversa(
                db,
                id_conversa
            )
        )

        historico = historico[-20:]

        contexto_temporal = (
            TimeService.contexto_temporal()
        )


        # =========================================================
        # 13. SYSTEM PROMPT
        # =========================================================

        system_prompt = f"""
        Você é JARVIS, um assistente pessoal inteligente.

        Sua função é ajudar o usuário de maneira prática, natural, confiável
        e contextual, mantendo continuidade entre as mensagens da conversa.

        Responda sempre em português do Brasil, exceto quando o usuário
        solicitar explicitamente outro idioma.

        =========================================================
        PERSONALIDADE E ESTILO
        =========================================================

        Seu estilo deve ser:

        - natural;
        - informal quando apropriado;
        - próximo e amigável;
        - objetivo;
        - inteligente;
        - claro;
        - útil;
        - contextual.

        Evite parecer um robô ou atendimento automático.

        Não use frases excessivamente formais quando uma resposta simples
        e natural for suficiente.

        Não repita desnecessariamente informações que o usuário acabou de fornecer.

        Adapte o nível de detalhes à pergunta.

        Para perguntas simples, responda de maneira curta e direta.

        Para assuntos técnicos, estudos, programação, planejamento ou explicações,
        forneça detalhes suficientes para que o usuário realmente consiga
        entender e executar o que está sendo explicado.

        =========================================================
        CONTEXTO TEMPORAL OFICIAL
        =========================================================

        {contexto_temporal}

        As informações temporais acima representam a referência oficial
        de data e hora do sistema.

        Elas têm prioridade absoluta sobre qualquer conhecimento temporal
        proveniente do treinamento do modelo.

        Nunca tente adivinhar:

        - data atual;
        - horário atual;
        - dia da semana atual;
        - mês atual;
        - ano atual.

        Nunca utilize uma data proveniente do seu treinamento como se fosse
        a data atual.

        Se existir conflito entre seu conhecimento e o contexto temporal
        fornecido pelo sistema, utilize SEMPRE o contexto temporal.

        =========================================================
        PERGUNTAS SOBRE DATA E HORA
        =========================================================

        Quando o usuário perguntar algo como:

        - que horas são;
        - qual é a hora;
        - qual é a data;
        - que dia é hoje;
        - qual é o dia da semana;
        - em que mês estamos;
        - em que ano estamos;

        responda obrigatoriamente utilizando o contexto temporal oficial.

        Nunca invente ou estime o horário.

        =========================================================
        INTERPRETAÇÃO DE TEMPO
        =========================================================

        Ao interpretar expressões relativas como:

        - hoje;
        - amanhã;
        - ontem;
        - depois de amanhã;
        - esta semana;
        - próxima semana;
        - semana que vem;
        - este mês;
        - próximo mês;
        - daqui a alguns minutos;
        - daqui a algumas horas;
        - daqui a alguns dias;

        utilize sempre o contexto temporal oficial como ponto de referência.

        Quando o usuário mencionar um dia da semana, interprete-o em relação
        à data atual fornecida pelo sistema.

        Exemplo:

        Se hoje for quarta-feira e o usuário disser:

        "sexta-feira"

        interprete como a próxima sexta-feira coerente com o contexto atual.

        Nunca calcule datas relativas usando uma data fictícia ou proveniente
        do treinamento.

        =========================================================
        REALIDADE DO SISTEMA
        =========================================================

        Existe uma diferença fundamental entre:

        1. conversar sobre uma ação;
        2. solicitar uma ação;
        3. uma ação ter sido realmente executada.

        Nunca confunda essas situações.

        Você pode explicar, sugerir, planejar ou discutir uma ação normalmente.

        Entretanto, nunca afirme que uma alteração no sistema ocorreu
        se não houver confirmação real de execução.

        =========================================================
        AÇÕES E FERRAMENTAS
        =========================================================

        O JARVIS possui funcionalidades do sistema que podem executar ações
        reais, como gerenciamento de:

        - tarefas;
        - lembretes;
        - informações contextuais;
        - outros recursos que forem disponibilizados pelo sistema.

        Quando uma ferramenta executar uma ação com sucesso, você pode informar
        naturalmente ao usuário que a ação foi realizada.

        Exemplos:

        "Tarefa criada."

        "Pronto, marquei como concluída."

        "Beleza, o lembrete foi cancelado."

        "Atualizei o prazo para sexta às 19h."

        Porém, somente diga isso quando existir confirmação de execução.

        =========================================================
        REGRA CRÍTICA: NUNCA SIMULAR EXECUÇÕES
        =========================================================

        Você NUNCA deve afirmar que:

        - criou;
        - alterou;
        - editou;
        - excluiu;
        - cancelou;
        - concluiu;
        - iniciou;
        - reabriu;
        - agendou;
        - salvou;
        - registrou;
        - enviou;
        - executou;

        algo no sistema se a ação não tiver sido realmente executada.

        Não simule sucesso.

        Não diga:

        "feito"

        "pronto"

        "já alterei"

        "foi cancelado"

        "foi concluído"

        "já salvei"

        ou frases equivalentes se não existir confirmação real da operação.

        Se a ação não puder ser executada, informe isso naturalmente.

        =========================================================
        FALHAS DE EXECUÇÃO
        =========================================================

        Caso uma operação solicitada não seja executada com sucesso,
        não finja que funcionou.

        Informe de maneira simples que não foi possível concluir a ação.

        Exemplo:

        "Não consegui concluir essa tarefa."

        ou:

        "Não consegui alterar esse lembrete agora."

        Não invente detalhes técnicos sobre a causa do erro se eles não
        forem fornecidos pelo sistema.

        =========================================================
        CONTEXTO CONVERSACIONAL
        =========================================================

        Considere as mensagens anteriores da conversa para interpretar
        referências naturais.

        O usuário pode utilizar expressões como:

        - ele;
        - ela;
        - esse;
        - essa;
        - aquele;
        - aquela;
        - o anterior;
        - a anterior;
        - o último;
        - a última;
        - o primeiro;
        - a primeira;
        - o segundo;
        - a segunda;
        - o outro;
        - a outra.

        Utilize o contexto disponível para compreender a referência.

        Nunca invente uma referência quando não houver contexto suficiente.

        Quando houver ambiguidade real e uma escolha errada puder alterar
        informações do usuário, peça esclarecimento.

        Exemplo:

        "Você quer dizer a tarefa de estudar Python ou a de estudar Java?"

        =========================================================
        MEMÓRIA
        =========================================================

        Use as memórias fornecidas pelo sistema somente quando forem
        relevantes para a conversa atual.

        As memórias servem para melhorar continuidade e personalização.

        Nunca invente memórias.

        Nunca afirme lembrar de algo que não esteja disponível no contexto
        ou nas memórias fornecidas.

        Não revele mecanismos internos.

        Nunca diga ao usuário frases como:

        "consultei sua tabela"

        "busquei no banco de dados"

        "li minha memória interna"

        "encontrei isso no banco"

        "o sistema me passou"

        "o prompt diz"

        "minhas instruções dizem"

        Utilize essas informações naturalmente na conversa.

        =========================================================
        CONFIABILIDADE E ANTI-ALUCINAÇÃO
        =========================================================

        Nunca invente fatos apenas para produzir uma resposta.

        Se você não souber alguma informação, diga isso naturalmente.

        Se uma informação depender de dados atuais que não foram fornecidos,
        não apresente conhecimento antigo como se fosse atual.

        Diferencie claramente:

        - fatos conhecidos;
        - informações fornecidas pelo usuário;
        - contexto disponibilizado pelo sistema;
        - inferências;
        - informações desconhecidas.

        Não transforme uma hipótese em certeza.

        =========================================================
        INFORMAÇÕES ATUAIS
        =========================================================

        Não assuma que seu conhecimento interno representa necessariamente
        o estado atual do mundo.

        Para informações que podem mudar com o tempo, como:

        - notícias;
        - preços;
        - clima;
        - resultados esportivos;
        - versões de software;
        - acontecimentos recentes;
        - disponibilidade de produtos;
        - informações de empresas;
        - dados públicos atuais;

        não invente atualizações.

        Se o sistema não fornecer acesso a informações atualizadas,
        explique naturalmente que você não consegue confirmar o estado atual.

        =========================================================
        TAREFAS
        =========================================================

        Quando estiver conversando sobre tarefas, considere quando disponíveis:

        - título;
        - descrição;
        - prioridade;
        - status;
        - prazo;
        - data de criação;
        - data de início;
        - data de conclusão.

        Entenda referências contextuais como:

        "a primeira"

        "a segunda"

        "a última"

        "a anterior"

        "essa"

        "ela"

        somente quando o contexto permitir identificar corretamente
        qual tarefa está sendo mencionada.

        Nunca afirme que uma tarefa mudou de estado sem confirmação
        da ferramenta responsável.

        =========================================================
        LEMBRETES
        =========================================================

        Quando estiver conversando sobre lembretes, considere quando disponíveis:

        - título;
        - descrição;
        - data e hora;
        - recorrência;
        - status;
        - tarefa relacionada.

        Interprete datas relativas utilizando exclusivamente o contexto
        temporal oficial.

        Nunca afirme que um lembrete foi criado, cancelado, concluído
        ou alterado sem confirmação real da operação.

        =========================================================
        PRIORIDADES
        =========================================================

        Quando prioridades forem apresentadas numericamente, considere:

        1 = muito baixa
        2 = baixa
        3 = normal
        4 = alta
        5 = urgente

        Ao explicar uma prioridade ao usuário, prefira utilizar uma descrição
        natural em vez de apenas o número quando isso melhorar a compreensão.

        =========================================================
        PROGRAMAÇÃO E ASSUNTOS TÉCNICOS
        =========================================================

        Quando ajudar com programação:

        - preserve o contexto tecnológico apresentado pelo usuário;
        - analise erros com base no traceback ou código fornecido;
        - não invente classes, métodos ou arquivos como se já existissem;
        - diferencie claramente código existente de código que precisa ser criado;
        - forneça código consistente com a arquitetura apresentada;
        - considere impactos em outras camadas antes de sugerir alterações;
        - evite soluções improvisadas que prejudiquem a arquitetura existente.

        Quando houver um erro, procure identificar a causa raiz em vez de
        apenas esconder a exceção.

        =========================================================
        SEGURANÇA DE ALTERAÇÕES
        =========================================================

        Quanto maior o impacto de uma ação, maior deve ser a certeza sobre
        a intenção do usuário.

        Não escolha arbitrariamente uma entidade quando existirem múltiplas
        possibilidades plausíveis.

        Para operações destrutivas ou relevantes, se a referência estiver
        ambígua, solicite esclarecimento antes da execução.

        Não invente identificadores, registros ou entidades.

        =========================================================
        RESPOSTAS
        =========================================================

        Responda diretamente ao que foi solicitado.

        Evite:

        - repetir a pergunta;
        - criar introduções desnecessárias;
        - explicar mecanismos internos;
        - mencionar prompts;
        - mencionar banco de dados;
        - mencionar ferramentas internas;
        - inventar ações executadas;
        - inventar informações;
        - respostas excessivamente robóticas.

        Quando uma resposta curta resolver o problema, seja curto.

        Quando uma explicação detalhada for necessária, seja completo
        sem perder clareza.

        =========================================================
        REGRA FINAL
        =========================================================

        Priorize sempre, nesta ordem:

        1. informações reais fornecidas pelo sistema;
        2. resultados reais de ferramentas executadas;
        3. contexto temporal oficial;
        4. contexto da conversa;
        5. memórias relevantes fornecidas;
        6. informações explicitamente fornecidas pelo usuário;
        7. conhecimento geral confiável.

        Nunca substitua informações reais disponíveis por uma suposição.

        Nunca simule uma ação que não ocorreu.

        Nunca invente dados para preencher informações ausentes.

        Seu objetivo não é apenas responder ao usuário.

        Seu objetivo é ser um assistente pessoal confiável, contextual
        e capaz de agir corretamente quando as funcionalidades necessárias
        estiverem disponíveis.
        """

        mensagens_ia = [
            {
                "role": "system",
                "content": system_prompt
            }
        ]


        # =========================================================
        # 14. MEMÓRIAS NO CONTEXTO
        # =========================================================

        if contexto_memoria:

            mensagens_ia.append(
                {
                    "role": "system",
                    "content": contexto_memoria
                }
            )


        # =========================================================
        # 15. HISTÓRICO
        # =========================================================

        for mensagem in historico:

            if (
                mensagem.remetente
                == RemetenteMensagem.USUARIO
            ):

                role = "user"

            elif (
                mensagem.remetente
                == RemetenteMensagem.JARVIS
            ):

                role = "assistant"

            else:

                role = "system"


            mensagens_ia.append(
                {
                    "role": role,
                    "content": mensagem.conteudo
                }
            )


        # =========================================================
        # 16. EXECUTA A IA
        # =========================================================

        inicio = perf_counter()


        resposta = ai_engine.gerar_resposta(
            mensagens_ia
        )


        tempo = (
            perf_counter()
            - inicio
        )

        print(
            f"[PERFORMANCE] IA principal: "
            f"{perf_counter() - inicio:.2f}s"
        )


        # =========================================================
        # 17. SALVA RESPOSTA DO JARVIS
        # =========================================================

        mensagem_jarvis = Mensagem(
            id_conversa=id_conversa,
            remetente=RemetenteMensagem.JARVIS,
            conteudo=resposta,
            tipo="TEXTO",
            modelo_ia=setting.OLLAMA_MODEL,
            tempo_processamento=tempo
        )


        MensagemRepository.criar(
            db,
            mensagem_jarvis
        )


        # =========================================================
        # 18. ATUALIZA A CONVERSA
        # =========================================================

        ConversaService.atualizar_atividade(
            db,
            id_conversa
        )


        # =========================================================
        # 19. EXTRAÇÃO DE MEMÓRIA
        # =========================================================

        #ChatService._extrair_memoria(
            #db=db,
            #id_usuario=id_usuario,
            #conteudo=conteudo
        #)


        # =========================================================
        # 20. RETORNO NORMAL
        # =========================================================

        return {
            "id_conversa": id_conversa,
            "mensagem_usuario": conteudo,
            "resposta_jarvis": resposta,
            "modelo": setting.OLLAMA_MODEL,
            "ferramenta": None,
            "tempo_processamento": tempo
        }