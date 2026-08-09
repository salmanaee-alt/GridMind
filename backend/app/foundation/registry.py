from __future__ import annotations

from app.foundation.exceptions import (
    EngineNotFoundError,
    EngineRegistrationError,
)
from app.foundation.interfaces import (
    Engine,
)


class EngineRegistry:
    """
    Registry of Foundation engines.
    """

    def __init__(self) -> None:
        self._engines: dict[
            str,
            Engine,
        ] = {}

    def register(
        self,
        engine: Engine,
    ) -> None:
        name = engine.metadata.name

        if name in self._engines:
            raise EngineRegistrationError(
                f"Engine already registered: {name}"
            )

        self._engines[name] = engine

    def resolve(
        self,
        name: str,
    ) -> Engine:
        try:
            return self._engines[name]

        except KeyError as exc:
            raise EngineNotFoundError(
                f"Engine not found: {name}"
            ) from exc

    def exists(
        self,
        name: str,
    ) -> bool:
        return name in self._engines

    def unregister(
        self,
        name: str,
    ) -> None:
        if name not in self._engines:
            raise EngineNotFoundError(
                f"Engine not found: {name}"
            )

        del self._engines[name]

    def clear(
        self,
    ) -> None:
        self._engines.clear()

    def list(
        self,
    ) -> tuple[str, ...]:
        return tuple(
            sorted(
                self._engines
            )
        )

    def count(
        self,
    ) -> int:
        return len(
            self._engines
        )