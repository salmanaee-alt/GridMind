from __future__ import annotations

from pydantic import (
    BaseModel,
    ConfigDict,
)


class ThroughFaultContext(
    BaseModel,
):
    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
    )

    upstream_protection_operated: bool | None = None

    downstream_protection_operated: bool | None = None

    transformer_breakers_opened: bool | None = None

    high_through_fault_current_detected: bool | None = None

    shadow_only: bool = True
    affects_reasoning: bool = False
    affects_decision: bool = False