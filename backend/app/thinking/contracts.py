from __future__ import annotations

from enum import Enum
from typing import Any, Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)
from app.thinking.graph_context import (
    ThinkingGraphContext,
)


class FrozenThinkingModel(BaseModel):
    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
    )


class ThinkingStage(str, Enum):
    OBSERVE = "observe"
    UNDERSTAND = "understand"
    VALIDATE = "validate"
    HYPOTHESIZE = "hypothesize"
    RANK_EVIDENCE = "rank_evidence"
    RESOLVE_CONFLICTS = "resolve_conflicts"
    VERIFY_PHYSICS = "verify_physics"
    SAFETY_GATE = "safety_gate"
    DECIDE = "decide"
    EXPLAIN = "explain"
    LEARN = "learn"
    COMPLETED = "completed"


class ThinkingStageRecord(FrozenThinkingModel):
    stage: ThinkingStage

    completed: bool = False

    summary: str = ""

    data: dict[str, Any] = Field(
        default_factory=dict,
    )


class ThinkingState(FrozenThinkingModel):
    session_id: str = Field(
        min_length=1,
    )

    current_stage: ThinkingStage = (
        ThinkingStage.OBSERVE
    )

    graph_context: ThinkingGraphContext = (
    ThinkingGraphContext()
    )

    observations: tuple[Any, ...] = ()

    evidence: tuple[Any, ...] = ()

    hypotheses: tuple[Any, ...] = ()

    physics_checks: tuple[Any, ...] = ()

    safety_findings: tuple[Any, ...] = ()

    decisions: tuple[Any, ...] = ()

    explanations: tuple[Any, ...] = ()

    learning_items: tuple[Any, ...] = ()

    stage_history: tuple[
        ThinkingStageRecord,
        ...,
    ] = ()

    metadata: dict[str, Any] = Field(
        default_factory=dict,
    )

    shadow_only: Literal[True] = True

    affects_reasoning: Literal[False] = False

    affects_decision: Literal[False] = False