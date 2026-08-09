from __future__ import annotations

from typing import Protocol

from app.foundation.context import (
    ExecutionContext,
)
from app.foundation.metadata import (
    EngineMetadata,
)
from app.foundation.results import (
    EngineResult,
)


class Engine(Protocol):
    """
    Unified contract implemented by every runtime engine.
    """

    @property
    def metadata(self) -> EngineMetadata:
        ...

    def execute(
        self,
        context: ExecutionContext,
    ) -> EngineResult:
        ...