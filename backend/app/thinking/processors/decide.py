from __future__ import annotations

from app.thinking.contracts import (
    ThinkingStage,
    ThinkingState,
)


class DecideProcessor:
    stage = ThinkingStage.DECIDE

    def execute(
        self,
        state: ThinkingState,
    ) -> ThinkingState:
        decision_count = len(
            state.decisions
        )

        has_decisions = (
            decision_count > 0
        )

        return state.model_copy(
            update={
                "metadata": {
                    **state.metadata,
                    "decide_stage": {
                        "decision_count": (
                            decision_count
                        ),
                        "has_decisions": (
                            has_decisions
                        ),
                        "decision_status": (
                            "available"
                            if has_decisions
                            else "not_available"
                        ),
                        "advisory_only": True,
                        "execution_authorized": False,
                    },
                }
            }
        )