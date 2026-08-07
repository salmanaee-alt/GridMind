from __future__ import annotations

from app.thinking.contracts import (
    ThinkingStage,
    ThinkingState,
)


class UnderstandProcessor:
    stage = ThinkingStage.UNDERSTAND

    def execute(
        self,
        state: ThinkingState,
    ) -> ThinkingState:
        evidence_count = len(
            state.evidence
        )

        hypothesis_count = len(
            state.hypotheses
        )

        return state.model_copy(
            update={
                "metadata": {
                    **state.metadata,
                    "understand_stage": {
                        "evidence_count": (
                            evidence_count
                        ),
                        "hypothesis_count": (
                            hypothesis_count
                        ),
                        "has_engineering_context": (
                            bool(
                                state.observations
                                or state.evidence
                                or state.hypotheses
                            )
                        ),
                    },
                }
            }
        )