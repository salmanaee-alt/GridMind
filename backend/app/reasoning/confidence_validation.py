from __future__ import annotations

from app.foundation.results import (
    EngineResult,
)
from app.reasoning.confidence_contracts import (
    ConfidencePropagationResult,
)


def validate_confidence_result(
    result: EngineResult,
) -> bool:
    return (
        isinstance(
            result.payload,
            ConfidencePropagationResult,
        )
        and result.shadow_only
        and not result.affects_reasoning
        and not result.affects_decision
    )