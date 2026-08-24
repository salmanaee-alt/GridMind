from __future__ import annotations

from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
)

from app.transformer.ct_saturation_contracts import (
    CTSaturationIndicators,
)


CTSaturationStatus = Literal[
    "supported",
    "not_supported",
    "insufficient_evidence",
]


class CTSaturationEvaluation(
    BaseModel,
):
    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
    )

    status: CTSaturationStatus

    confirmed: bool = False

    shadow_only: bool = True
    affects_reasoning: bool = False
    affects_decision: bool = False


def evaluate_ct_saturation(
    indicators: CTSaturationIndicators,
) -> CTSaturationEvaluation:
    values = (
        indicators.waveform_asymmetry_detected,
        indicators.secondary_current_distortion_detected,
        indicators.high_through_fault_current_detected,
    )

    known_values = [
        value
        for value in values
        if value is not None
    ]

    if not known_values:
        status: CTSaturationStatus = (
            "insufficient_evidence"
        )
    elif len(known_values) < 2:
        status = "insufficient_evidence"
    elif all(
        value is False
        for value in known_values
    ):
        status = "not_supported"
    elif all(
        value is True
        for value in known_values
    ) and len(known_values) == 3:
        status = "supported"
    else:
        status = "insufficient_evidence"

    return CTSaturationEvaluation(
        status=status,
    )