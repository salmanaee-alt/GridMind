from __future__ import annotations

from app.foundation.context import (
    ExecutionContext,
)
from app.foundation.metadata import (
    EngineMetadata,
)
from app.foundation.results import (
    EngineResult,
)
from app.foundation.types import (
    ExecutionStatus,
)
from app.reasoning.confidence_contracts import (
    ConfidencePropagationResult,
)


class ConfidencePropagationEngine:
    """
    Foundation-compliant shell for confidence propagation.

    The propagation algorithm is intentionally not implemented
    here because no approved propagation rule currently exists
    in repository code or ADRs.
    """

    @property
    def metadata(self) -> EngineMetadata:
        return EngineMetadata(
            name="confidence_propagation",
            version="0.1.0",
            description=(
                "Confidence propagation reasoning engine"
            ),
            category="reasoning",
            experimental=True,
        )

    def execute(
        self,
        context: ExecutionContext,
    ) -> EngineResult:
        payload = ConfidencePropagationResult()

        return EngineResult(
            status=ExecutionStatus.SKIPPED,
            payload=payload,
            execution_summary=(
                "Confidence propagation skipped because "
                "no approved propagation algorithm is "
                "currently defined."
            ),
        )