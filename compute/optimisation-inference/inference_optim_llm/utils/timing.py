"""
inference_optim_llm.utils.timing
================================

Outils de chronométrage légers, sans dépendance externe, utilisables
autant dans du code synchrone que dans des coroutines *async*.

Fonctionnalités :
-----------------
- chrono : context‐manager synchrone qui expose une fonction
  `elapsed()` pour récupérer la durée en secondes.
- chrono_async : équivalent asynchrone à utiliser dans un
  `async with`.
- timeit / timeit_async : décorateurs pour profiler facilement
  des fonctions ou coroutines ; la durée est retournée dans un tuple
  `(résultat, elapsed)`, ou loggée si un logger est fourni.

Tous les temps sont mesurés en utilisant `time.perf_counter()`
(haute résolution, monotone).
"""

from __future__ import annotations

import asyncio
import contextlib
import functools
import logging
import time
import types
import typing as _t

__all__ = [
    "chrono",
    "chrono_async",
    "timeit",
    "timeit_async",
]

# --------------------------------------------------------------------------- #
# Contexte synchrone
# --------------------------------------------------------------------------- #


@contextlib.contextmanager
def chrono() -> _t.Iterator[_t.Callable[[], float]]:
    """
    Context-manager simple :

    ```python
    with chrono() as t:
        heavy_computation()
    print(f"latence : {t():.3f}s")
    ```

    `t()` peut être appelé autant de fois que souhaité après la sortie
    du bloc (« lazy »).
    """
    start = time.perf_counter()
    yield lambda: time.perf_counter() - start


# --------------------------------------------------------------------------- #
# Contexte asynchrone
# --------------------------------------------------------------------------- #


class _AsyncChrono:
    def __init__(self) -> None:
        self._start: float | None = None

    async def __aenter__(self) -> _t.Callable[[], float]:
        # On ne fait pas de pause I/O ici, mais respecter la signature async
        self._start = time.perf_counter()
        return lambda: time.perf_counter() - _t.cast(float, self._start)

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: types.TracebackType | None,
    ) -> bool | None:
        # Propager d’éventuelles exceptions (return False)
        return None


def chrono_async() -> _AsyncChrono:
    """
    Version asynchrone :

    ```python
    async with chrono_async() as t:
        await call_remote_api()
    logger.info("temps appel remote = %.2fs", t())
    ```
    """
    return _AsyncChrono()


# --------------------------------------------------------------------------- #
# Décorateurs utilitaires
# --------------------------------------------------------------------------- #


def _decorate(func: _t.Callable[..., _t.Any], logger: logging.Logger | None = None):
    """
    Fabrique un décorateur pour fonction *synchrone*.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):  # type: ignore[override]
        with chrono() as t:
            result = func(*args, **kwargs)
        if logger:
            logger.debug("timeit | %s took %.4fs", func.__qualname__, t())
        return result, t()

    return wrapper


def timeit(logger: logging.Logger | None = None):
    """
    Décorateur de mesure pour fonctions synchrones.

    ```python
    @timeit(logger)
    def foo(x):
        ...
        return value

    value, elapsed = foo(42)
    ```
    """

    def decorator(func: _t.Callable[..., _t.Any]):
        return _decorate(func, logger)

    return decorator


def timeit_async(logger: logging.Logger | None = None):
    """
    Décorateur de mesure pour coroutines / fonctions async.

    Retourne (result, elapsed) comme `timeit`.

    ```python
    @timeit_async()
    async def bar():
        await asyncio.sleep(0.1)

    result, dt = await bar()
    ```
    """

    def decorator(func: _t.Callable[..., _t.Any]):
        if not asyncio.iscoroutinefunction(func):
            raise TypeError("timeit_async s’utilise uniquement sur des coroutines.")

        @functools.wraps(func)
        async def wrapper(*args, **kwargs):  # type: ignore[override]
            async with chrono_async() as t:
                result = await func(*args, **kwargs)
            if logger:
                logger.debug("timeit_async | %s took %.4fs", func.__qualname__, t())
            return result, t()

        return wrapper

    return decorator
