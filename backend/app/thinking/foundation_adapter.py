from __future__ import annotations

from time import perf_counter

from app.foundation.context import (
    ExecutionContext,
)
from app.foundation.diagnostics import (
    EngineDiagnostics,
)
from app.foundation.metadata import (
    EngineMetadata,
)
from app.foundation.results import (
    EngineResult,
)
from app.foundation.types import (
    ExecutionStatus,
)
from app.thinking.contracts import (
    ThinkingStage,
    ThinkingState,
)
from app.thinking.engine import (
    EngineeringThinkingEngine,
)


THINKING_STATE_RESOURCE_KEY = (
    "thinking_state"
)


class ThinkingFoundationAdapter:
    """
    Foundation adapter for the outer EngineeringThinkingEngine boundary.

    The adapter does not modify the native Thinking pipeline,
    stage processors, or ThinkingState contract.
    """

    def __init__(
        self,
        *,
        engine: EngineeringThinkingEngine,
    ) -> None:
        if not isinstance(
            engine,
            EngineeringThinkingEngine,
        ):
            raise TypeError(
                "engine must be an "
                "EngineeringThinkingEngine."
            )

        self._engine = engine

    @property
    def metadata(
        self,
    ) -> EngineMetadata:
        return EngineMetadata(
            name="engineering_thinking",
            version="1.0.0",
            description=(
                "Foundation adapter for the "
                "engineering thinking pipeline."
            ),
            category="thinking",
            experimental=True,
        )

    def execute(
        self,
        context: ExecutionContext,
    ) -> EngineResult:
        state = context.resources.get(
            THINKING_STATE_RESOURCE_KEY
        )

        if state is None:
            raise ValueError(
                "ExecutionContext.resources is missing "
                f"{THINKING_STATE_RESOURCE_KEY!r}."
            )

        if not isinstance(
            state,
            ThinkingState,
        ):
            raise TypeError(
                f"{THINKING_STATE_RESOURCE_KEY!r} "
                "must contain a ThinkingState."
            )

        started_at = perf_counter()

        final_state = self._engine.execute(
            state
        )

        duration_ms = round(
            max(
                0.0,
                (
                    perf_counter()
                    - started_at
                )
                * 1000,
            ),
            3,
        )

        if (
            final_state.shadow_only is not True
            or final_state.affects_reasoning is not False
            or final_state.affects_decision is not False
        ):
            raise ValueError(
                "ThinkingState violates the native "
                "safety contract."
            )

        status = (
            ExecutionStatus.SUCCESS
            if final_state.current_stage
            == ThinkingStage.COMPLETED
            else ExecutionStatus.FAILED
        )

        stage_names = tuple(
            record.stage.value
            for record in final_state.stage_history
        )

        diagnostics = EngineDiagnostics(
            processed_items=len(
                final_state.stage_history
            ),
            execution_time_ms=duration_ms,
            traceability=(
                final_state.session_id,
                *stage_names,
            ),
        )

        return EngineResult(
            status=status,
            payload={
                "current_stage":
                    final_state.current_stage.value,
                "stage_history": [
                    record.stage.value
                    for record in final_state.stage_history
                ],
                "metadata":
                    final_state.metadata,
            },
            diagnostics=diagnostics,
            metadata={
                "session_id":
                    final_state.session_id,
            },
            execution_summary=(
                "Engineering thinking pipeline "
                f"completed with status "
                f"{status.value}."
            ),
        )