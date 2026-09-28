import re
import unicodedata


class CapabilityResponseGuard:

    # =========================================================
    # NORMALIZAÇÃO
    # =========================================================

    @staticmethod
    def _normalizar(
        texto: str | None
    ) -> str:

        if not texto:
            return ""

        texto = unicodedata.normalize(
            "NFKD",
            str(texto)
        )

        texto = "".join(
            caractere
            for caractere in texto
            if not unicodedata.combining(
                caractere
            )
        )

        return texto.lower().strip()

    # =========================================================
    # DETECTA CONSULTA SOBRE NOTIFICAÇÃO / VOZ
    # =========================================================

    @staticmethod
    def _consulta_notificacao(
        mensagem_usuario: str
    ) -> bool:

        texto = (
            CapabilityResponseGuard
            ._normalizar(
                mensagem_usuario
            )
        )

        termos = (
            "avisar",
            "avisa",
            "avisado",
            "avisada",
            "notificar",
            "notificacao",
            "alerta",
            "por voz",
            "voz",
            "quando o lembrete",
            "quando chegar",
            "quando der a hora",
            "automaticamente",
            "automatico"
        )

        return any(
            termo in texto
            for termo in termos
        )

    # =========================================================
    # DETECTA PROMESSA DE CAPACIDADE INEXISTENTE
    # =========================================================

    @staticmethod
    def _promete_notificacao_automatica(
        resposta_modelo: str
    ) -> bool:

        texto = (
            CapabilityResponseGuard
            ._normalizar(
                resposta_modelo
            )
        )

        padroes = (
            r"\beu (?:te )?notificarei\b",
            r"\beu (?:te )?avisarei\b",
            r"\bvou (?:te )?notificar\b",
            r"\bvou (?:te )?avisar\b",
            r"\bsera notificad[oa]\b",
            r"\bsera avisad[oa]\b",
            r"\bnotificarei (?:voce|aqui)\b",
            r"\bavisarei (?:voce|aqui)\b",
            r"\bquando .* chegar.* notific",
            r"\bquando .* chegar.* avis",
            r"\bquando .* horario .* notific",
            r"\bquando .* horario .* avis",
            r"\bnotificarei aqui\b",
            r"\bavisarei aqui\b",
            r"\bquando .* chega.* notific",
            r"\bquando .* chega.* avis",
            r"\bnotifica voce aqui\b",
            r"\bavisa voce aqui\b"
        )

        return any(
            re.search(
                padrao,
                texto
            )
            for padrao in padroes
        )

    # =========================================================
    # VALIDAÇÃO
    # =========================================================

    @staticmethod
    def validar(
        mensagem_usuario: str,
        resposta_modelo: str
    ) -> str:

        if not resposta_modelo:
            return resposta_modelo

        if not (
            CapabilityResponseGuard
            ._promete_notificacao_automatica(
                resposta_modelo
            )
        ):
            return resposta_modelo

        if (
            CapabilityResponseGuard
            ._consulta_notificacao(
                mensagem_usuario
            )
        ):
            return (
                "Não. Atualmente não tenho capacidade de emitir "
                "avisos por voz nem notificações automáticas. "
                "Posso criar e gerenciar lembretes, mas o sistema "
                "ainda não dispara alertas sozinho quando o horário "
                "do lembrete chega."
            )

        return (
            "Um lembrete é um registro usado para guardar algo que "
            "você deseja lembrar em uma data ou horário específico. "
            "Na A.R.A., posso criar, consultar, editar, cancelar e "
            "concluir lembretes. Atualmente, porém, o sistema ainda "
            "não dispara notificações automáticas quando o horário chega."
        )