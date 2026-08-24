from app.transformer.ct_saturation_contracts import (
    CTSaturationIndicators,
)
from app.transformer.ct_saturation_evaluator import (
    evaluate_ct_saturation,
)


def test_ct_saturation_supported_with_all_indicators():
    result = evaluate_ct_saturation(
        CTSaturationIndicators(
            waveform_asymmetry_detected=True,
            secondary_current_distortion_detected=True,
            high_through_fault_current_detected=True,
        )
    )

    assert result.status == "supported"
    assert result.shadow_only is True
    assert result.affects_reasoning is False
    assert result.affects_decision is False


def test_ct_saturation_not_supported_when_indicators_are_negative():
    result = evaluate_ct_saturation(
        CTSaturationIndicators(
            waveform_asymmetry_detected=False,
            secondary_current_distortion_detected=False,
            high_through_fault_current_detected=False,
        )
    )

    assert result.status == "not_supported"


def test_ct_saturation_insufficient_without_indicators():
    result = evaluate_ct_saturation(
        CTSaturationIndicators()
    )

    assert result.status == "insufficient_evidence"


def test_single_indicator_is_insufficient():
    result = evaluate_ct_saturation(
        CTSaturationIndicators(
            waveform_asymmetry_detected=True,
        )
    )

    assert result.status == "insufficient_evidence"


def test_supported_ct_saturation_is_not_confirmed():
    result = evaluate_ct_saturation(
        CTSaturationIndicators(
            waveform_asymmetry_detected=True,
            secondary_current_distortion_detected=True,
            high_through_fault_current_detected=True,
        )
    )

    assert result.status == "supported"
    assert result.confirmed is False


def test_ct_saturation_evaluation_never_claims_confirmation():
    cases = [
        CTSaturationIndicators(),
        CTSaturationIndicators(
            waveform_asymmetry_detected=False,
            secondary_current_distortion_detected=False,
            high_through_fault_current_detected=False,
        ),
        CTSaturationIndicators(
            waveform_asymmetry_detected=True,
            secondary_current_distortion_detected=True,
            high_through_fault_current_detected=True,
        ),
    ]

    for indicators in cases:
        result = evaluate_ct_saturation(
            indicators
        )

        assert result.confirmed is False