from __future__ import annotations

from typing import Any

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
)


class ConfidenceCalibrationPolicy(
    BaseModel,
):
    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
    )

    policy_id: str = Field(
        min_length=1,
    )

    version: str = Field(
        min_length=1,
    )

    approved: bool = False

    validation_dataset_id: str | None = None

    calibration_method: str | None = None

    calibration_metrics: dict[
        str,
        Any,
    ] = Field(
        default_factory=dict,
    )

    permits_probability_output: bool = False

    permits_propagation_seed: bool = False

    shadow_only: bool = True
    affects_reasoning: bool = False
    affects_decision: bool = False

    @model_validator(mode="after")
    def validate_approval_requirements(
        self,
    ) -> "ConfidenceCalibrationPolicy":
        if not self.approved:
            return self

        if not self.validation_dataset_id:
            raise ValueError(
                "approved calibration policy requires "
                "validation_dataset_id."
            )

        if not self.calibration_method:
            raise ValueError(
                "approved calibration policy requires "
                "calibration_method."
            )

        if not self.calibration_metrics:
            raise ValueError(
                "approved calibration policy requires "
                "calibration_metrics."
            )

        return self