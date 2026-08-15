from __future__ import annotations

from typing import Any, Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


CAPABILITY_ABI_VERSION = "1.0"

CapabilityStatus = Literal[
    "success",
    "error",
    "skipped",
]


class FrozenCapabilityModel(BaseModel):
    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
    )


class CapabilityRequest(FrozenCapabilityModel):
    request_id: str = Field(
        min_length=1,
        max_length=200,
    )
    payload: dict[str, Any] = Field(
        default_factory=dict,
    )
    context: dict[str, Any] = Field(
        default_factory=dict,
    )


class CapabilityMetadata(FrozenCapabilityModel):
    capability_id: str = Field(
        pattern=r"^CAP-[A-Z0-9]{2,20}-[0-9]{4,}$"
    )
    name: str = Field(
        min_length=1,
        max_length=200,
    )
    version: str = Field(
        pattern=r"^[0-9]+\.[0-9]+\.[0-9]+$"
    )
    abi_version: str = Field(
        pattern=r"^[0-9]+\.[0-9]+$"
    )
    shadow_only: Literal[True] = True
    affects_decision: Literal[False] = False


class CapabilityResult(FrozenCapabilityModel):
    capability_id: str = Field(
        pattern=r"^CAP-[A-Z0-9]{2,20}-[0-9]{4,}$"
    )
    status: CapabilityStatus
    output: dict[str, Any] = Field(
        default_factory=dict,
    )
    audit: dict[str, Any] = Field(
        default_factory=dict,
    )
    affects_decision: Literal[False] = False

class CapabilityExecutionRecord(FrozenCapabilityModel):
    """
    Standard audit record for every capability execution.

    This model contains execution metadata only.
    It must never contain engineering decisions.
    """

    capability_id: str = Field(
        pattern=r"^CAP-[A-Z0-9]{2,20}-[0-9]{4,}$"
    )
    status: CapabilityStatus
    execution_mode: Literal["shadow"]
    affects_decision: Literal[False] = False
    duration_ms: float = Field(
        ge=0,
    )
    error: dict[str, Any] | None = None