from pydantic import ValidationError
import pytest

from app.transformer.ct_saturation_contracts import (
    CTSaturationIndicators,
)


def test_ct_saturation_indicators_accept_valid_input():
    indicators = CTSaturationIndicators(
        waveform_asymmetry_detected=True,
        secondary_current_distortion_detected=True,
        high_through_fault_current_detected=True,
    )

    assert (
        indicators.waveform_asymmetry_detected
        is True
    )
    assert (
        indicators.secondary_current_distortion_detected
        is True
    )
    assert (
        indicators.high_through_fault_current_detected
        is True
    )


def test_ct_saturation_indicators_default_to_unknown():
    indicators = CTSaturationIndicators()

    assert (
        indicators.waveform_asymmetry_detected
        is None
    )
    assert (
        indicators.secondary_current_distortion_detected
        is None
    )
    assert (
        indicators.high_through_fault_current_detected
        is None
    )


def test_ct_saturation_indicators_are_shadow_only():
    indicators = CTSaturationIndicators()

    assert indicators.shadow_only is True
    assert indicators.affects_reasoning is False
    assert indicators.affects_decision is False


def test_ct_saturation_indicators_forbid_extra_fields():
    with pytest.raises(ValidationError):
        CTSaturationIndicators(
            invented_indicator=True,
        )
