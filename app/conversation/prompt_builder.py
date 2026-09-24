from app.conversation.response_policy import (
    PoliticaMarkdown,
    ResponseProfile,
    TamanhoResposta
)


class PromptBuilder:

    # =====================================================
    # POLÍTICA DE TAMANHO
    # =====================================================

    @staticmethod
    def _instrucao_tamanho(
        perfil: ResponseProfile
    ) -> str:

        if (
            perfil.tamanho
            == TamanhoResposta.CURTA
        ):
            return (
                "Responda de forma curta e direta. "
                "Em perguntas simples, prefira de 1 a 3 frases. "
                "Não prolongue a resposta apenas para parecer mais completa."
            )

        if (
            perfil.tamanho
            == TamanhoResposta.DETALHADA
        ):
            return (
                "O usuário pediu uma resposta detalhada. "
                "Explique com profundidade suficiente, mantendo clareza "
                "e evitando repetição desnecessária."
            )

        return (
            "Responda com o nível de detalhe necessário para resolver "
            "a solicitação, sem excesso de texto."
        )

    # =====================================================
    # POLÍTICA DE MARKDOWN
    # =====================================================

    @staticmethod
    def _instrucao_markdown(
        perfil: ResponseProfile
    ) -> str:

        if (
            perfil.markdown
            == PoliticaMarkdown.MINIMO
        ):
            return (
                "Use Markdown somente quando realmente necessário. "
                "Não use títulos, negrito, itálico ou listas apenas "
                "por estética. Respostas simples devem parecer uma "
                "conversa natural."
            )

        return (
            "Você pode usar Markdown quando ele melhorar a compreensão, "
            "especialmente em código, passos, comparações ou conteúdo "
            "técnico. Não exagere na formatação."
        )

    # =====================================================
    # COMPORTAMENTO GERAL
    # =====================================================

    @staticmethod
    def _instrucao_comportamento() -> str:

        return (
            "Não use um bordão fixo para iniciar respostas. "
            "Evite repetir expressões como 'Fechou!', 'Beleza!', "
            "'Boa!' ou 'Pronto!' em todas as interações. "
            "Uma resposta pode começar diretamente pela informação "
            "ou resultado relevante. "
            "Varie a linguagem naturalmente quando houver motivo, "
            "sem parecer aleatório ou artificial. "
            "Não repita a pergunta do usuário antes de responder. "
            "Não acrescente encerramentos genéricos como "
            "'se precisar de mais alguma coisa' quando isso não for útil."
        )

    # =====================================================
    # TRATAMENTO
    # =====================================================

    @staticmethod
    def _instrucao_tratamento() -> str:

        return (
            "Adapte o tratamento ao contexto da conversa. "
            "Em situações técnicas, seja focada e precisa. "
            "Em conversas casuais, pode ser mais próxima e natural. "
            "Em situações sensíveis ou importantes, use um tom mais "
            "cuidadoso e sóbrio. "
            "Não finja possuir emoções humanas; demonstre adequação "
            "por meio da linguagem e do nível de atenção."
        )

    # =====================================================
    # CONSTRUIR POLÍTICA CONVERSACIONAL
    # =====================================================

    @staticmethod
    def construir_politica(
        perfil: ResponseProfile
    ) -> str:

        partes = [
            PromptBuilder._instrucao_tamanho(
                perfil
            ),
            PromptBuilder._instrucao_markdown(
                perfil
            ),
            PromptBuilder._instrucao_comportamento(),
            PromptBuilder._instrucao_tratamento()
        ]

        return "\n".join(
            partes
        )