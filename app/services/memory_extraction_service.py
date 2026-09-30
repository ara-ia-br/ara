from time import perf_counter

from sqlalchemy.orm import Session

from app.memory.memory_extractor import MemoryExtractor


class MemoryExtractionService:

    @staticmethod
    def processar(
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