from __future__ import annotations

from typing import Any


EXPECTED_REASONING_STAGES = (
    "observe",
    "understand",
    "validate",
    "hypothesize",
    "reason",
    "evaluate",
    "decide",
    "explain",
    "learn",
)


def build_reasoning_trace_audit(
    reasoning_steps: list[Any],
) -> dict[str, Any]:
    """
    Audit the structural integrity of an engineering
    reasoning trace.

    This function is descriptive and audit-only.
    It does not modify reasoning, confidence, ranking,
    safety state, readiness, or engineering decisions.
    """

    observed_stages = [
        step.get("stage")
        for step in reasoning_steps
        if isinstance(step, dict)
        and isinstance(step.get("stage"), str)
    ]

    missing_stages = [
        stage
        for stage in EXPECTED_REASONING_STAGES
        if stage not in observed_stages
    ]

    duplicate_stages = [
        stage
        for stage in EXPECTED_REASONING_STAGES
        if observed_stages.count(stage) > 1
    ]

    unknown_stages = [
        stage
        for stage in observed_stages
        if stage not in EXPECTED_REASONING_STAGES
    ]

    expected_observed_order = [
        stage
        for stage in observed_stages
        if stage in EXPECTED_REASONING_STAGES
    ]

    order_valid = (
        expected_observed_order
        == list(EXPECTED_REASONING_STAGES)
    )

    trace_complete = (
        not missing_stages
        and not duplicate_stages
        and not unknown_stages
        and order_valid
    )

    return {
        "status": (
            "complete"
            if trace_complete
            else "incomplete"
        ),
        "expected_stages": list(
            EXPECTED_REASONING_STAGES
        ),
        "observed_stages": observed_stages,
        "missing_stages": missing_stages,
        "duplicate_stages": duplicate_stages,
        "unknown_stages": unknown_stages,
        "order_valid": order_valid,
        "trace_complete": trace_complete,
        "affects_confidence": False,
        "affects_ranking": False,
        "affects_decision": False,
    }
