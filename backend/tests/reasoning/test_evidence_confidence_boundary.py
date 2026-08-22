import pytest

from pydantic import ValidationError

from app.reasoning.evidence_confidence_boundary import (
    EvidenceConfidenceAssessment,
    assess_evidence_confidence,
)


def test_evidence_confidence_is_uncalibrated_by_default():
    assessment = assess_evidence_confidence(
        evidence_id="physics:differential_current",
        confidence=1.0,
    )

    assert assessment.confidence == pytest.approx(
        1.0
    )
    assert (
        assessment.is_calibrated_probability
        is False
    )
    assert (
        assessment.usable_as_propagation_seed
        is False
    )


def test_numeric_confidence_is_not_automatically_probability():
    assessment = assess_evidence_confidence(
        evidence_id="relay:event",
        confidence=0.80,
    )

    assert assessment.confidence == pytest.approx(
        0.80
    )
    assert (
        assessment.is_calibrated_probability
        is False
    )
    assert assessment.calibrated_probability is None


def test_evidence_confidence_assessment_is_shadow_only():
    assessment = assess_evidence_confidence(
        evidence_id="relay:event",
        confidence=0.80,
    )

    assert assessment.shadow_only is True
    assert assessment.affects_reasoning is False
    assert assessment.affects_decision is False


def test_evidence_confidence_requires_explicit_evidence_id():
    with pytest.raises(ValidationError):
        EvidenceConfidenceAssessment(
            evidence_id="",
            confidence=0.80,
        )


@pytest.mark.parametrize(
    "confidence",
    [
        -0.01,
        1.01,
        True,
        False,
    ],
)
def test_evidence_confidence_rejects_invalid_values(
    confidence,
):
    with pytest.raises(ValidationError):
        EvidenceConfidenceAssessment(
            evidence_id="relay:event",
            confidence=confidence,
        )