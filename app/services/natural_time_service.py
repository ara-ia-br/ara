import re

from datetime import (
    datetime,
    timedelta
)

from app.services.time_service import (
    TimeService
)


class NaturalTimeService:

    DIAS_SEMANA = {
        "segunda": 0,
        "segunda-feira": 0,

        "terca": 1,
        "terça": 1,
        "terca-feira": 1,
        "terça-feira": 1,

        "quarta": 2,
        "quarta-feira": 2,

        "quinta": 3,
        "quinta-feira": 3,

        "sexta": 4,
        "sexta-feira": 4,

        "sabado": 5,
        "sábado": 5,

        "domingo": 6
    }


    # =========================================================
    # INTERPRETAR DATA/HORA NATURAL
    # =========================================================

    @staticmethod
    def interpretar(
        texto: str
    ) -> datetime | None:

        if not texto:
            return None

        texto = texto.lower().strip()

        agora = TimeService.agora()


        # =====================================================
        # 1. DAQUI A X MINUTOS
        # =====================================================

        match = re.search(
            r"\bdaqui\s+a\s+(\d+)\s+minutos?\b",
            texto
        )

        if match:

            minutos = int(
                match.group(1)
            )

            return agora + timedelta(
                minutes=minutos
            )


        # =====================================================
        # 2. DAQUI A X HORAS
        # =====================================================

        match = re.search(
            r"\bdaqui\s+a\s+(\d+)\s+horas?\b",
            texto
        )

        if match:

            horas = int(
                match.group(1)
            )

            return agora + timedelta(
                hours=horas
            )


        # =====================================================
        # 3. DAQUI A X DIAS
        # =====================================================

        match = re.search(
            r"\bdaqui\s+a\s+(\d+)\s+dias?\b",
            texto
        )

        if match:

            dias = int(
                match.group(1)
            )

            return agora + timedelta(
                days=dias
            )


        # =====================================================
        # 4. DEFINE DATA BASE
        # =====================================================

        data_base = None


        # =====================================================
        # 5. DEPOIS DE AMANHÃ
        # =====================================================

        if (
            "depois de amanhã" in texto
            or "depois de amanha" in texto
        ):

            data_base = agora + timedelta(
                days=2
            )


        # =====================================================
        # 6. AMANHÃ
        # =====================================================

        elif (
            "amanhã" in texto
            or "amanha" in texto
        ):

            data_base = agora + timedelta(
                days=1
            )


        # =====================================================
        # 7. HOJE
        # =====================================================

        elif "hoje" in texto:

            data_base = agora


        # =====================================================
        # 8. DATA DD/MM/YYYY
        # =====================================================

        match_data = re.search(
            r"\b"
            r"(\d{1,2})/"
            r"(\d{1,2})/"
            r"(\d{4})"
            r"\b",
            texto
        )

        if match_data:

            dia = int(
                match_data.group(1)
            )

            mes = int(
                match_data.group(2)
            )

            ano = int(
                match_data.group(3)
            )

            try:

                data_base = agora.replace(
                    year=ano,
                    month=mes,
                    day=dia
                )

            except ValueError:

                raise ValueError(
                    "A data informada é inválida."
                )


        # =====================================================
        # 9. DATA DD/MM
        # =====================================================

        elif data_base is None:

            match_data_curta = re.search(
                r"\b"
                r"(\d{1,2})/"
                r"(\d{1,2})"
                r"\b",
                texto
            )

            if match_data_curta:

                dia = int(
                    match_data_curta.group(1)
                )

                mes = int(
                    match_data_curta.group(2)
                )

                ano = agora.year

                try:

                    data_base = agora.replace(
                        year=ano,
                        month=mes,
                        day=dia
                    )

                except ValueError:

                    raise ValueError(
                        "A data informada é inválida."
                    )

                # Se a data já passou,
                # considera o próximo ano.
                if data_base < agora:

                    try:

                        data_base = (
                            data_base.replace(
                                year=ano + 1
                            )
                        )

                    except ValueError:

                        raise ValueError(
                            "A data informada é inválida."
                        )


        # =====================================================
        # 10. DIA DA SEMANA
        # =====================================================

        if data_base is None:

            # Ordena nomes maiores primeiro.
            dias_ordenados = sorted(
                NaturalTimeService
                .DIAS_SEMANA
                .items(),
                key=lambda item: len(
                    item[0]
                ),
                reverse=True
            )

            for nome_dia, numero_dia in dias_ordenados:

                if re.search(
                    rf"\b{re.escape(nome_dia)}\b",
                    texto
                ):

                    dia_atual = agora.weekday()

                    diferenca = (
                        numero_dia
                        - dia_atual
                    ) % 7

                    # Se hoje for o mesmo dia,
                    # assume a próxima ocorrência.
                    if diferenca == 0:
                        diferenca = 7

                    data_base = (
                        agora
                        + timedelta(
                            days=diferenca
                        )
                    )

                    break


        # =====================================================
        # 11. SEM DATA
        # =====================================================

        if data_base is None:
            return None


        # =====================================================
        # 12. HORÁRIO COM "ÀS"
        #
        # Ex:
        # às 19h
        # às 19:30
        # as 20h
        # =====================================================

        horario = re.search(
            r"\b(?:às|as|a)\s+"
            r"([01]?\d|2[0-3])"
            r"(?:[:h](\d{2}))?"
            r"\s*(?:h|horas?)?\b",
            texto,
            flags=re.IGNORECASE
        )


        # =====================================================
        # 13. HORÁRIO HH:MM / HHh / HHhMM
        # =====================================================

        if horario is None:

            horario = re.search(
                r"\b"
                r"([01]?\d|2[0-3])"
                r"(?:[:h](\d{2}))"
                r"\s*(?:h|horas?)?"
                r"\b",
                texto
            )


        if horario:

            hora = int(
                horario.group(1)
            )

            minuto = int(
                horario.group(2)
                or 0
            )


        # =====================================================
        # 14. MANHÃ
        # =====================================================

        elif (
            "de manhã" in texto
            or "de manha" in texto
            or "pela manhã" in texto
            or "pela manha" in texto
        ):

            hora = 8
            minuto = 0


        # =====================================================
        # 15. TARDE
        # =====================================================

        elif (
            "à tarde" in texto
            or "a tarde" in texto
            or "pela tarde" in texto
        ):

            hora = 15
            minuto = 0


        # =====================================================
        # 16. NOITE
        # =====================================================

        elif (
            "à noite" in texto
            or "a noite" in texto
            or "pela noite" in texto
        ):

            hora = 19
            minuto = 0


        # =====================================================
        # 17. SEM HORÁRIO EXPLÍCITO
        # =====================================================

        else:

            hora = 9
            minuto = 0


        # =====================================================
        # 18. RESULTADO FINAL
        # =====================================================

        resultado = data_base.replace(
            hour=hora,
            minute=minuto,
            second=0,
            microsecond=0
        )

        return resultado


    # =========================================================
    # REMOVER EXPRESSÕES TEMPORAIS DO TÍTULO
    # =========================================================

    @staticmethod
    def remover_tempo_do_texto(
        texto: str
    ) -> str:

        if not texto:
            return ""

        resultado = texto


        # =====================================================
        # 1. EXPRESSÕES RELATIVAS MAIORES PRIMEIRO
        # =====================================================

        padroes = [

            # Depois de amanhã vem antes de amanhã
            r"\bdepois\s+de\s+amanhã\b",
            r"\bdepois\s+de\s+amanha\b",

            r"\bamanhã\b",
            r"\bamanha\b",

            r"\bhoje\b",


            # =================================================
            # DAQUI A X
            # =================================================

            r"\bdaqui\s+a\s+\d+\s+minutos?\b",

            r"\bdaqui\s+a\s+\d+\s+horas?\b",

            r"\bdaqui\s+a\s+\d+\s+dias?\b",


            # =================================================
            # DATAS
            # =================================================

            r"\b\d{1,2}/\d{1,2}/\d{4}\b",

            r"\b\d{1,2}/\d{1,2}\b",


            # =================================================
            # DIAS DA SEMANA
            #
            # Nomes completos SEMPRE antes dos curtos.
            # =================================================

            r"\bsegunda-feira\b",
            r"\bsegunda\b",

            r"\bterça-feira\b",
            r"\bterca-feira\b",
            r"\bterça\b",
            r"\bterca\b",

            r"\bquarta-feira\b",
            r"\bquarta\b",

            r"\bquinta-feira\b",
            r"\bquinta\b",

            r"\bsexta-feira\b",
            r"\bsexta\b",

            r"\bsábado\b",
            r"\bsabado\b",

            r"\bdomingo\b",


            # =================================================
            # HORÁRIO COM PREPOSIÇÃO
            #
            # às 19h
            # as 19:30
            # a 20h
            # =================================================

            r"\b(?:às|as|a)\s+"
            r"([01]?\d|2[0-3])"
            r"(?:[:h]\d{2})?"
            r"\s*(?:h|horas?)?\b",


            # =================================================
            # HH:MM
            # =================================================

            r"\b"
            r"([01]?\d|2[0-3])"
            r":\d{2}"
            r"\b",


            # =================================================
            # HHhMM / HHh
            # =================================================

            r"\b"
            r"([01]?\d|2[0-3])"
            r"h(?:\d{2})?"
            r"\b",


            # =================================================
            # PARTES DO DIA
            # =================================================

            r"\bde manhã\b",
            r"\bde manha\b",

            r"\bpela manhã\b",
            r"\bpela manha\b",

            r"\bà tarde\b",
            r"\ba tarde\b",
            r"\bpela tarde\b",

            r"\bà noite\b",
            r"\ba noite\b",
            r"\bpela noite\b"
        ]


        # =====================================================
        # 2. REMOVE PADRÕES
        # =====================================================

        for padrao in padroes:

            resultado = re.sub(
                padrao,
                "",
                resultado,
                flags=re.IGNORECASE
            )


        # =====================================================
        # 3. NORMALIZA ESPAÇOS
        # =====================================================

        resultado = re.sub(
            r"\s+",
            " ",
            resultado
        )

        resultado = resultado.strip(
            " ,.!?;:-"
        )


        # =====================================================
        # 4. REMOVE PREPOSIÇÕES TEMPORAIS QUE SOBRARAM NO FINAL
        #
        # Ex:
        #
        # estudar python para sexta às 19h
        #
        # depois da remoção:
        #
        # estudar python para
        #
        # resultado:
        #
        # estudar python
        # =====================================================

        resultado = re.sub(
            r"\s+\b("
            r"para|"
            r"até|"
            r"ate|"
            r"em|"
            r"no|"
            r"na|"
            r"às|"
            r"as"
            r")\s*$",
            "",
            resultado,
            flags=re.IGNORECASE
        )


        # =====================================================
        # 5. REMOVE "PARA" REPETIDO/ISOLADO
        #
        # Ex:
        #
        # "para estudar python para"
        #
        # vira primeiro:
        #
        # "para estudar python"
        #
        # O "_limpar_titulo()" do Agent remove o
        # "para" inicial depois.
        # =====================================================

        resultado = re.sub(
            r"\s+\bpara\s*$",
            "",
            resultado,
            flags=re.IGNORECASE
        )


        # =====================================================
        # 6. NORMALIZA NOVAMENTE
        # =====================================================

        resultado = re.sub(
            r"\s+",
            " ",
            resultado
        )

        resultado = resultado.strip(
            " ,.!?;:-"
        )


        return resultado