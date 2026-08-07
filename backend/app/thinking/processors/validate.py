from __future__ import annotations

from app.thinking.contracts import (
    ThinkingStage,
    ThinkingState,
)


class ValidateProcessor:
    stage = ThinkingStage.VALIDATE

    def execute(
        self,
        state: ThinkingState,
    ) -> ThinkingState:
        evidence_count = len(
            state.evidence
        )

        has_evidence = evidence_count > 0

        return state.model_copy(
            update={
                "metadata": {
                    **state.metadata,
                    "validate_stage": {
                        "evidence_count": (
                            evidence_count
                        ),
                        "has_evidence": (
                            has_evidence
                        ),
                        "validation_status": (
                            "available"
                            if has_evidence
                            else "insufficient"
                        ),
                    },
                }
            }
        )