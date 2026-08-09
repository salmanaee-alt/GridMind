from __future__ import annotations

from datetime import (
    UTC,
    datetime,
)
from typing import Any
from uuid import uuid4

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


class ExecutionContext(BaseModel):
    """
    Domain-agnostic runtime context passed to Foundation engines.

    Foundation does not import EngineeringSession, ThinkingState,
    GraphContext, or any engineering-domain type directly.
    """

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
    )

    correlation_id: str = Field(
        default_factory=lambda: str(
            uuid4()
        ),
        min_length=1,
    )

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(
            UTC
        ),
    )

    resources: dict[str, Any] = Field(
        default_factory=dict,
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict,
    )