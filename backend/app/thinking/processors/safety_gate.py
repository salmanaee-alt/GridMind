from __future__ import annotations

from typing import Any

from app.thinking.contracts import (
    ThinkingStage,
    ThinkingState,
)


def _extract_severity(
    finding: Any,
) -> str | None:
    if not isinstance(finding, dict):
        return None

    value = finding.get("severity")

    if isinstance(value, str):
        return value.strip().lower()

    return None


class SafetyGateProcessor:
    stage = ThinkingStage.SAFETY_GATE

    def execute(
        self,
        state: ThinkingState,
    ) -> ThinkingState:
        low_count = 0
        medium_count = 0
        high_count = 0
        critical_count = 0
        unknown_count = 0

        for finding in state.safety_findings:
            severity = _extract_severity(
                finding
            )

            if severity == "low":
                low_count += 1
            elif severity == "medium":
                medium_count += 1
            elif severity == "high":
                high_count += 1
            elif severity == "critical":
                critical_count += 1
            else:
                unknown_count += 1

        finding_count = len(
            state.safety_findings
        )

        if finding_count == 0:
            safety_status = "not_available"
        elif critical_count > 0:
            safety_status = "critical_findings"
        elif high_count > 0:
            safety_status = "high_findings"
        elif medium_count > 0:
            safety_status = "medium_findings"
        elif unknown_count > 0:
            safety_status = "incomplete"
        else:
            safety_status = "no_blocking_findings"

        return state.model_copy(
            update={
                "metadata": {
                    **state.metadata,
                    "safety_gate_stage": {
                        "finding_count": finding_count,
                        "low_count": low_count,
                        "medium_count": medium_count,
                        "high_count": high_count,
                        "critical_count": critical_count,
                        "unknown_count": unknown_count,
                        "safety_status": safety_status,
                        "advisory_only": True,
                    },
                }
            }
        )