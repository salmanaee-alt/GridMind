from __future__ import annotations

from typing import (
    Any,
    Literal,
)

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)

from app.foundation.diagnostics import (
    EngineDiagnostics,
)
from app.foundation.types import (
    ExecutionStatus,
)


class EngineResult(BaseModel):
    """
    Immutable result returned by every Foundation engine.
    """

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
    )

    status: ExecutionStatus

    payload: Any | None = None

    diagnostics: EngineDiagnostics = Field(
        default_factory=EngineDiagnostics,
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict,
    )

    execution_summary: str | None = None

    shadow_only: Literal[True] = True

    affects_reasoning: Literal[False] = False

    affects_decision: Literal[False] = False