from __future__ import annotations

from dataclasses import dataclass

from app.thinking.contracts import (
    ThinkingStage,
    ThinkingStageRecord,
    ThinkingState,
)
from app.thinking.stages import (
    ThinkingStageProcessor,
)


_STAGE_ORDER = (
    ThinkingStage.OBSERVE,
    ThinkingStage.UNDERSTAND,
    ThinkingStage.VALIDATE,
    ThinkingStage.HYPOTHESIZE,
    ThinkingStage.RANK_EVIDENCE,
    ThinkingStage.RESOLVE_CONFLICTS,
    ThinkingStage.VERIFY_PHYSICS,
    ThinkingStage.SAFETY_GATE,
    ThinkingStage.DECIDE,
    ThinkingStage.EXPLAIN,
    ThinkingStage.LEARN,
)


@dataclass(frozen=True)
class EngineeringThinkingEngine:
    processors: tuple[
        ThinkingStageProcessor,
        ...,
    ] = ()

    def execute(
        self,
        state: ThinkingState,
    ) -> ThinkingState:
        current_state = state

        processor_by_stage = {
            processor.stage: processor
            for processor in self.processors
        }

        for stage in _STAGE_ORDER:
            processor = processor_by_stage.get(stage)

            if processor is not None:
                current_state = processor.execute(
                    current_state
                )

            current_state = self._complete_stage(
                current_state,
                stage,
            )

        return current_state.model_copy(
            update={
                "current_stage": (
                    ThinkingStage.COMPLETED
                )
            }
        )

    def _complete_stage(
        self,
        state: ThinkingState,
        stage: ThinkingStage,
    ) -> ThinkingState:
        record = ThinkingStageRecord(
            stage=stage,
            completed=True,
            summary=(
                f"{stage.value} stage completed."
            ),
        )

        return state.model_copy(
            update={
                "current_stage": stage,
                "stage_history": (
                    *state.stage_history,
                    record,
                ),
            }
        )