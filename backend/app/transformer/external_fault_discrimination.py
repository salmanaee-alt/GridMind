from __future__ import annotations

from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
)

from app.transformer.physics_contracts import (
    DifferentialOperatingRegionSummary,
)


ExternalFaultDiscriminationStatus = Literal[
    "supported",
    "insufficient_evidence",
]


class ExternalFaultDiscriminationEvaluation(
    BaseModel,
):
    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
    )

    status: ExternalFaultDiscriminationStatus

    confirmed: bool = False

    shadow_only: bool = True
    affects_reasoning: bool = False
    affects_decision: bool = False


def evaluate_external_fault_discrimination(
    *,
    operating_region:
        DifferentialOperatingRegionSummary | None,
    ct_saturation_status: str | None,
) -> ExternalFaultDiscriminationEvaluation:
    if (
        operating_region is not None
        and operating_region.any_phase_operate
        and ct_saturation_status == "supported"
    ):
        status: ExternalFaultDiscriminationStatus = (
            "supported"
        )
    else:
        status = "insufficient_evidence"

    return ExternalFaultDiscriminationEvaluation(
        status=status,
    )