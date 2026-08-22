from __future__ import annotations

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)

from app.brain.evidence_contracts import (
    EvidenceValidity,
)


class ConfidenceSeedEligibilityAssessment(
    BaseModel,
):
    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
    )

    evidence_id: str = Field(
        min_length=1,
    )

    validity: EvidenceValidity

    is_calibrated_probability: bool

    candidate_for_seed: bool

    usable_as_propagation_seed: bool = False

    shadow_only: bool = True
    affects_reasoning: bool = False
    affects_decision: bool = False


def assess_seed_eligibility(
    *,
    evidence_id: str,
    validity: EvidenceValidity,
    is_calibrated_probability: bool,
) -> ConfidenceSeedEligibilityAssessment:
    candidate_for_seed = (
        validity == EvidenceValidity.VALID
    )

    return ConfidenceSeedEligibilityAssessment(
        evidence_id=evidence_id,
        validity=validity,
        is_calibrated_probability=(
            is_calibrated_probability
        ),
        candidate_for_seed=(
            candidate_for_seed
        ),
        usable_as_propagation_seed=False,
    )