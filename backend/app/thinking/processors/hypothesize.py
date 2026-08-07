from __future__ import annotations

from app.thinking.contracts import (
    ThinkingStage,
    ThinkingState,
)


class HypothesizeProcessor:
    stage = ThinkingStage.HYPOTHESIZE

    def execute(
        self,
        state: ThinkingState,
    ) -> ThinkingState:
        hypothesis_count = len(
            state.hypotheses
        )

        has_hypotheses = (
            hypothesis_count > 0
        )

        return state.model_copy(
            update={
                "metadata": {
                    **state.metadata,
                    "hypothesize_stage": {
                        "hypothesis_count": (
                            hypothesis_count
                        ),
                        "has_hypotheses": (
                            has_hypotheses
                        ),
                        "generation_status": (
                            "available"
                            if has_hypotheses
                            else "not_generated"
                        ),
                    },
                }
            }
        )