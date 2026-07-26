from app.brain.engineering_brain import EngineeringBrain


def _hypothesis(confidence: str = "high") -> dict:
    return {
        "hypothesis": "Internal transformer fault",
        "confidence": confidence,
        "supporting_evidence": ["Differential relay operated"],
        "missing_evidence": ["COMTRADE waveform"],
        "conflicts": [],
    }


def test_confidence_audit_declares_qualitative_confidence():
    hypothesis = _hypothesis()

    EngineeringBrain()._attach_confidence_calibration_status(
        [hypothesis]
    )

    audit = hypothesis["confidence_calibration"]

    assert audit["confidence"] == "high"
    assert audit["confidence_type"] == "qualitative"
    assert audit["is_calibrated_probability"] is False
    assert audit["calibrated_probability"] is None


def test_confidence_calibration_status_is_audit_only():
    hypothesis = _hypothesis("medium")
    original_confidence = hypothesis["confidence"]

    EngineeringBrain()._attach_confidence_calibration_status(
        [hypothesis]
    )

    audit = hypothesis["confidence_calibration"]

    assert hypothesis["confidence"] == original_confidence
    assert audit["affects_confidence"] is False
    assert audit["affects_ranking"] is False
    assert audit["affects_decision"] is False


def test_confidence_rank_is_not_exposed_as_probability():
    hypothesis = _hypothesis("high")

    EngineeringBrain()._attach_confidence_calibration_status(
        [hypothesis]
    )

    audit = hypothesis["confidence_calibration"]

    assert audit["confidence_rank"] == 3
    assert audit["calibrated_probability"] is None
    assert audit["confidence_rank"] != audit["calibrated_probability"]


def test_unknown_confidence_remains_uncalibrated():
    hypothesis = _hypothesis("unknown")

    EngineeringBrain()._attach_confidence_calibration_status(
        [hypothesis]
    )

    audit = hypothesis["confidence_calibration"]

    assert audit["confidence_rank"] == 0
    assert audit["is_calibrated_probability"] is False
    assert audit["calibrated_probability"] is None
    