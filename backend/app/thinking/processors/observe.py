from __future__ import annotations

from app.thinking.contracts import (
    ThinkingStage,
    ThinkingState,
)


class ObserveProcessor:
    stage = ThinkingStage.OBSERVE

    def execute(
        self,
        state: ThinkingState,
    ) -> ThinkingState:
        observation_count = len(
            state.observations
        )

        return state.model_copy(
            update={
                "metadata": {
                    **state.metadata,
                    "observe_stage": {
                        "observation_count": (
                            observation_count
                        ),
                        "has_observations": (
                            observation_count > 0
                        ),
                    },
                }
            }
        )