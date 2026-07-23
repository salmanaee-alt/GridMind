from __future__ import annotations

from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


class CapabilityPipelineStep(BaseModel):
    """
    Declarative definition of one capability
    inside an execution pipeline.

    This model contains orchestration policy only.
    It contains no engineering reasoning.
    """

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
    )

    capability_id: str = Field(
        pattern=r"^CAP-[A-Z0-9]{2,20}-[0-9]{4,}$"
    )

    required: bool = True

    execution_mode: Literal["shadow"] = "shadow"

    depends_on: tuple[str, ...] = ()


class CapabilityPipelinePolicy(BaseModel):
    """
    Ordered capability execution policy.

    Pipeline order is explicit and deterministic.
    """

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
    )

    pipeline_id: str = Field(
        min_length=1,
        max_length=100,
    )

    version: str = Field(
        pattern=r"^[0-9]+\.[0-9]+\.[0-9]+$"
    )

    steps: tuple[CapabilityPipelineStep, ...] = ()