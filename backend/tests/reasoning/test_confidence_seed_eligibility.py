import pytest

from app.brain.evidence_contracts import (
    EvidenceValidity,
)
from app.reasoning.confidence_seed_eligibility import (
    assess_seed_eligibility,
)


@pytest.mark.parametrize(
    "validity",
    [
        EvidenceValidity.INVALID,
        EvidenceValidity.UNKNOWN,
        EvidenceValidity.INSUFFICIENT,
    ],
)
def test_non_valid_evidence_is_not_seed_candidate(
    validity,
):
    assessment = assess_seed_eligibility(
        evidence_id="evidence:0",
        validity=validity,
        is_calibrated_probability=False,
    )

    assert assessment.candidate_for_seed is False
    assert assessment.usable_as_propagation_seed is False


def test_valid_evidence_can_be_seed_candidate():
    assessment = assess_seed_eligibility(
        evidence_id="evidence:0",
        validity=EvidenceValidity.VALID,
        is_calibrated_probability=False,
    )

    assert assessment.candidate_for_seed is True


def test_candidate_is_not_automatically_usable_seed():
    assessment = assess_seed_eligibility(
        evidence_id="evidence:0",
        validity=EvidenceValidity.VALID,
        is_calibrated_probability=False,
    )

    assert assessment.candidate_for_seed is True
    assert assessment.usable_as_propagation_seed is False


def test_uncalibrated_evidence_cannot_be_used_as_seed():
    assessment = assess_seed_eligibility(
        evidence_id="evidence:0",
        validity=EvidenceValidity.VALID,
        is_calibrated_probability=False,
    )

    assert assessment.is_calibrated_probability is False
    assert assessment.usable_as_propagation_seed is False


def test_seed_eligibility_is_shadow_only():
    assessment = assess_seed_eligibility(
        evidence_id="evidence:0",
        validity=EvidenceValidity.VALID,
        is_calibrated_probability=False,
    )

    assert assessment.shadow_only is True
    assert assessment.affects_reasoning is False
    assert assessment.affects_decision is False