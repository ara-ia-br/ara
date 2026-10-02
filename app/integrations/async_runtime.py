from __future__ import annotations

import asyncio
import threading
from concurrent.futures import (
    TimeoutError as FutureTimeoutError,
)
from typing import Awaitable, TypeVar


T = TypeVar("T")


class AsyncIntegrationRuntime:
    """
    Executa integrações assíncronas a partir do pipeline
    síncrono atual da A.R.A.

    Um único event loop é mantido em uma thread dedicada.

    Isso permite preservar:
    - caches;
    - locks assíncronos;
    - conexões futuras;
    - providers externos.

    Sem transformar todo o ChatService em async.
    """

    _loop: asyncio.AbstractEventLoop | None = None
    _thread: threading.Thread | None = None

    _ready = threading.Event()
    _start_lock = threading.Lock()

    # =========================================================
    # INICIAR
    # =========================================================

    @classmethod
    def _garantir_iniciado(
        cls
    ) -> None:

        if (
            cls._thread is not None
            and cls._thread.is_alive()
            and cls._loop is not None
        ):
            return

        with cls._start_lock:

            if (
                cls._thread is not None
                and cls._thread.is_alive()
                and cls._loop is not None
            ):
                return

            cls._ready.clear()

            cls._thread = threading.Thread(
                target=cls._executar_loop,
                name="ara-integrations-loop",
                daemon=True,
            )

            cls._thread.start()

        if not cls._ready.wait(
            timeout=5
        ):
            raise RuntimeError(
                "Não foi possível iniciar "
                "o runtime de integrações."
            )

        if cls._loop is None:
            raise RuntimeError(
                "Runtime de integrações "
                "não inicializado."
            )

    # =========================================================
    # EVENT LOOP
    # =========================================================

    @classmethod
    def _executar_loop(
        cls
    ) -> None:

        loop = asyncio.new_event_loop()

        asyncio.set_event_loop(
            loop
        )

        cls._loop = loop

        cls._ready.set()

        loop.run_forever()

    # =========================================================
    # EXECUTAR COROUTINE
    # =========================================================

    @classmethod
    def executar(
        cls,
        awaitable: Awaitable[T],
        timeout: float = 30.0,
    ) -> T:

        cls._garantir_iniciado()

        if cls._loop is None:
            raise RuntimeError(
                "Runtime de integrações indisponível."
            )

        future = (
            asyncio.run_coroutine_threadsafe(
                awaitable,
                cls._loop,
            )
        )

        try:

            return future.result(
                timeout=timeout
            )

        except FutureTimeoutError as erro:

            future.cancel()

            raise TimeoutError(
                "A integração excedeu "
                "o tempo limite."
            ) from erro