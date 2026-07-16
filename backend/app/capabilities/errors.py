from __future__ import annotations

from typing import Literal

from pydantic import Field

from app.capabilities.contracts import (
    FrozenCapabilityModel,
)


CapabilityErrorStage = Literal[
    "validate",
    "execute",
    "audit",
    "runtime",
]


class CapabilityError(FrozenCapabilityModel):
    error_type: str = Field(
        min_length=1,
        max_length=100,
    )
    message: str = Field(
        min_length=1,
        max_length=2000,
    )
    capability_id: str = Field(
        min_length=1,
        max_length=200,
    )
    request_id: str = Field(
        min_length=1,
        max_length=200,
    )
    stage: CapabilityErrorStage
    retryable: bool = False
