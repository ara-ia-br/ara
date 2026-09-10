from decimal import Decimal

from app.database.connection import SessionLocal
from app.memory.memory_consolidator import (
    MemoryConsolidator,
    MemoryConsolidationAction,
)
from app.models.memoria import Memoria


def limpar_memorias_teste(db, id_usuario: int):
    (
        db.query(Memoria)
        .filter(Memoria.id_usuario == id_usuario)
        .delete(synchronize_session=False)
    )
    db.commit()


def executar_testes():
    db = SessionLocal()

    # Use um ID de usuário REAL existente no seu banco.
    ID_USUARIO_TESTE = 1

    try:
        print("\n===================================")
        print(" TESTE MEMORY CONSOLIDATOR")
        print("===================================")

        limpar_memorias_teste(
            db,
            ID_USUARIO_TESTE
        )

        # ===============================================
        # TESTE 1 - CRIAR
        # ===============================================

        resultado1 = MemoryConsolidator.consolidar(
            db=db,
            id_usuario=ID_USUARIO_TESTE,
            tipo="PREFERENCIA",
            conteudo="Usuário prefere estudar à noite.",
            importancia=Decimal("70")
        )

        assert (
            resultado1.acao
            == MemoryConsolidationAction.CRIAR
        )

        assert resultado1.memoria is not None

        print(
            "TESTE 1 - criar nova memória: OK"
        )

        # ===============================================
        # TESTE 2 - REFORÇAR DUPLICATA EXATA
        # ===============================================

        resultado2 = MemoryConsolidator.consolidar(
            db=db,
            id_usuario=ID_USUARIO_TESTE,
            tipo="PREFERENCIA",
            conteudo="Usuário prefere estudar à noite.",
            importancia=Decimal("70")
        )

        assert (
            resultado2.acao
            == MemoryConsolidationAction.REFORCAR
        )

        assert resultado2.memoria is not None

        assert (
            resultado2.memoria.id_memoria
            == resultado1.memoria.id_memoria
        )

        print(
            "TESTE 2 - reforçar duplicata: OK"
        )

        # ===============================================
        # TESTE 3 - IMPORTÂNCIA AUMENTOU
        # ===============================================

        assert (
            Decimal(str(resultado2.memoria.importancia))
            > Decimal("70")
        )

        assert (
            Decimal(str(resultado2.memoria.importancia))
            <= Decimal("100")
        )

        print(
            "TESTE 3 - importância aumentada: OK"
        )

        # ===============================================
        # TESTE 4 - MEMÓRIA DIFERENTE
        # ===============================================

        resultado4 = MemoryConsolidator.consolidar(
            db=db,
            id_usuario=ID_USUARIO_TESTE,
            tipo="PREFERENCIA",
            conteudo="Usuário prefere trabalhar com Java.",
            importancia=Decimal("80")
        )

        assert (
            resultado4.acao
            == MemoryConsolidationAction.CRIAR
        )

        assert resultado4.memoria is not None

        assert (
            resultado4.memoria.id_memoria
            != resultado1.memoria.id_memoria
        )

        print(
            "TESTE 4 - memória diferente: OK"
        )

        # ===============================================
        # TESTE 5 - LIMITE DE IMPORTÂNCIA
        # ===============================================

        for _ in range(10):
            resultado5 = MemoryConsolidator.consolidar(
                db=db,
                id_usuario=ID_USUARIO_TESTE,
                tipo="PREFERENCIA",
                conteudo="Usuário prefere estudar à noite.",
                importancia=Decimal("100")
            )

        assert resultado5.memoria is not None

        assert (
            Decimal(str(resultado5.memoria.importancia))
            == Decimal("100")
        )

        print(
            "TESTE 5 - limite máximo 100: OK"
        )

        # ===============================================
        # RESULTADO
        # ===============================================

        print("\n===================================")
        print(" TODOS OS TESTES PASSARAM")
        print("===================================\n")

    finally:

        limpar_memorias_teste(
            db,
            ID_USUARIO_TESTE
        )

        db.close()


if __name__ == "__main__":
    executar_testes()