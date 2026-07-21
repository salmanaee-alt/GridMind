from __future__ import annotations

from typing import Iterable

from app.capabilities.runtime import CapabilityRuntime
from app.capabilities.runtime import CapabilityExecution


class CapabilityOrchestrator:
    """
    Executes capabilities in order.

    This class is intentionally lightweight.
    It contains no engineering reasoning and
    no decision-making logic.
    """

    def __init__(
        self,
        runtime: CapabilityRuntime,
    ) -> None:
        self._runtime = runtime

    def execute(
        self,
        executions: Iterable[tuple[str, object]],
    ) -> list[CapabilityExecution]:
        results: list[CapabilityExecution] = []

        for capability_id, request in executions:
            results.append(
                self._runtime.invoke(
                    capability_id=capability_id,
                    request=request,
                )
            )

        return results