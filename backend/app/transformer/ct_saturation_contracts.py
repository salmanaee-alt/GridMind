from __future__ import annotations

from pydantic import (
    BaseModel,
    ConfigDict,
)


class CTSaturationIndicators(
    BaseModel,
):
    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
    )

    waveform_asymmetry_detected: bool | None = None

    secondary_current_distortion_detected: bool | None = None

    high_through_fault_current_detected: bool | None = None

    shadow_only: bool = True
    affects_reasoning: bool = False
    affects_decision: bool = False

    