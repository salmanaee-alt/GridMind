from __future__ import annotations

from app.reasoning.confidence_contracts import (
    ConfidencePropagationResult,
)


def validate_confidence_result(
    result: ConfidencePropagationResult,
) -> bool:
    return (
        result.shadow_only
        and not result.affects_reasoning
        and not result.affects_decision
    )