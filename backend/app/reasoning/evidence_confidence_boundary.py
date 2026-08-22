from __future__ import annotations

from typing import Any

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)


class EvidenceConfidenceAssessment(BaseModel):
    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
    )

    evidence_id: str = Field(
        min_length=1,
    )

    confidence: float = Field(
        ge=0.0,
        le=1.0,
    )

    confidence_type: str = (
        "uncalibrated_numeric"
    )

    is_calibrated_probability: bool = False

    calibrated_probability: float | None = None

    usable_as_propagation_seed: bool = False

    shadow_only: bool = True
    affects_reasoning: bool = False
    affects_decision: bool = False

    @field_validator(
        "confidence",
        mode="before",
    )
    @classmethod
    def reject_boolean_confidence(
        cls,
        value: Any,
    ) -> Any:
        if isinstance(
            value,
            bool,
        ):
            raise ValueError(
                "evidence confidence must not be boolean."
            )

        return value


def assess_evidence_confidence(
    *,
    evidence_id: str,
    confidence: float,
) -> EvidenceConfidenceAssessment:
    return EvidenceConfidenceAssessment(
        evidence_id=evidence_id,
        confidence=confidence,
    )