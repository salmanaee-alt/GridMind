from __future__ import annotations

from typing import Any

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


class EngineDiagnostics(BaseModel):
    """
    Immutable diagnostics emitted by a Foundation engine.
    """

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
    )

    processed_items: int = Field(
        default=0,
        ge=0,
    )

    skipped_items: int = Field(
        default=0,
        ge=0,
    )

    execution_time_ms: float = Field(
        default=0.0,
        ge=0.0,
    )

    coverage: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )

    warnings: tuple[str, ...] = ()

    errors: tuple[str, ...] = ()

    traceability: tuple[str, ...] = ()

    metadata: dict[str, Any] = Field(
        default_factory=dict,
    )