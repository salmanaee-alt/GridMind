import pytest

from pydantic import ValidationError

from app.reasoning.confidence_calibration_policy import (
    ConfidenceCalibrationPolicy,
)


def test_calibration_policy_defaults_to_not_approved():
    policy = ConfidenceCalibrationPolicy(
        policy_id="CAL-001",
        version="0.1",
    )

    assert policy.approved is False
    assert policy.permits_probability_output is False
    assert policy.permits_propagation_seed is False


def test_calibration_policy_requires_validation_evidence_for_approval():
    with pytest.raises(ValidationError):
        ConfidenceCalibrationPolicy(
            policy_id="CAL-001",
            version="0.1",
            approved=True,
            validation_dataset_id=None,
            calibration_method=None,
            calibration_metrics={},
        )


def test_calibration_policy_requires_method_for_approval():
    with pytest.raises(ValidationError):
        ConfidenceCalibrationPolicy(
            policy_id="CAL-001",
            version="0.1",
            approved=True,
            validation_dataset_id="DATASET-001",
            calibration_method=None,
            calibration_metrics={
                "brier_score": 0.10,
            },
        )


def test_calibration_policy_does_not_permit_probability_by_default():
    policy = ConfidenceCalibrationPolicy(
        policy_id="CAL-001",
        version="0.1",
    )

    assert policy.permits_probability_output is False


def test_calibration_policy_is_shadow_only():
    policy = ConfidenceCalibrationPolicy(
        policy_id="CAL-001",
        version="0.1",
    )

    assert policy.shadow_only is True
    assert policy.affects_reasoning is False
    assert policy.affects_decision is False