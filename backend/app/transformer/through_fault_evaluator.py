from __future__ import annotations

from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
)

from app.transformer.through_fault_context import (
    ThroughFaultContext,
)


ThroughFaultStatus = Literal[
    "supported",
    "not_supported",
    "insufficient_evidence",
]


class ThroughFaultEvaluation(
    BaseModel,
):
    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
    )

    status: ThroughFaultStatus

    confirmed: bool = False

    shadow_only: bool = True
    affects_reasoning: bool = False
    affects_decision: bool = False


def evaluate_through_fault_context(
    context: ThroughFaultContext,
) -> ThroughFaultEvaluation:
    values = (
        context.upstream_protection_operated,
        context.downstream_protection_operated,
        context.transformer_breakers_opened,
        context.high_through_fault_current_detected,
    )

    known_values = [
        value
        for value in values
        if value is not None
    ]

    if not known_values:
        status: ThroughFaultStatus = (
            "insufficient_evidence"
        )
    elif len(known_values) < 2:
        status = "insufficient_evidence"
    elif all(
        value is False
        for value in known_values
    ):
        status = "not_supported"
    elif all(
        value is True
        for value in known_values
    ) and len(known_values) == 4:
        status = "supported"
    else:
        status = "insufficient_evidence"

    return ThroughFaultEvaluation(
        status=status,
    )