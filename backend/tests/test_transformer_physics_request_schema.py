from app.transformer.schemas import (
    TransformerDifferentialTripRequest,
)


def test_transformer_request_accepts_no_physics_inputs():
    request = TransformerDifferentialTripRequest()

    assert request.physics_measurements is None
    assert request.physics_context is None
    assert request.harmonic_measurement is None


def test_transformer_request_accepts_optional_physics_inputs():
    request = TransformerDifferentialTripRequest(
        physics_measurements={
            "hv_currents": {
                "phase_a": 100.0,
                "phase_b": 100.0,
                "phase_c": 100.0,
            },
            "lv_currents": {
                "phase_a": 1000.0,
                "phase_b": 1000.0,
                "phase_c": 1000.0,
            },
            "hv_ct_ratio": {
                "primary_a": 200.0,
                "secondary_a": 1.0,
            },
            "lv_ct_ratio": {
                "primary_a": 2000.0,
                "secondary_a": 1.0,
            },
            "hv_nominal_voltage_kv": 230.0,
            "lv_nominal_voltage_kv": 13.8,
        },
        physics_context={
            "vector_group": "Dyn11",
            "vector_group_compensation_applied": True,
        },
        harmonic_measurement={
            "fundamental_a": 100.0,
            "second_harmonic_a": 20.0,
            "fifth_harmonic_a": 5.0,
        },
    )

    assert request.physics_measurements is not None
    assert request.physics_context is not None
    assert request.harmonic_measurement is not None

    assert (
        request.physics_context.affects_decision
        is False
    )


def test_request_accepts_differential_characteristic_settings():
    request = TransformerDifferentialTripRequest(
        asset_id="T1",
        event_description=(
            "Transformer differential trip"
        ),
        differential_characteristic_settings={
            "pickup_a": 0.30,
            "slope": 0.25,
        },
    )

    settings = (
        request.differential_characteristic_settings
    )

    assert settings is not None
    assert settings.pickup_a == 0.30
    assert settings.slope == 0.25
    assert settings.affects_decision is False


def test_differential_characteristic_settings_are_optional():
    request = TransformerDifferentialTripRequest(
        asset_id="T1",
        event_description=(
            "Transformer differential trip"
        ),
    )

    assert (
        request.differential_characteristic_settings
        is None
    )


def test_request_accepts_ct_saturation_indicators():
    request = TransformerDifferentialTripRequest(
        asset_id="T1",
        event_description=(
            "Transformer differential trip"
        ),
        ct_saturation_indicators={
            "waveform_asymmetry_detected": True,
            "secondary_current_distortion_detected": True,
            "high_through_fault_current_detected": True,
        },
    )

    indicators = request.ct_saturation_indicators

    assert indicators is not None
    assert (
        indicators.waveform_asymmetry_detected
        is True
    )
    assert indicators.shadow_only is True
    assert indicators.affects_reasoning is False
    assert indicators.affects_decision is False


def test_ct_saturation_indicators_are_optional():
    request = TransformerDifferentialTripRequest(
        asset_id="T1",
        event_description=(
            "Transformer differential trip"
        ),
    )

    assert request.ct_saturation_indicators is None


def test_request_accepts_through_fault_context():
    request = TransformerDifferentialTripRequest(
        asset_id="T1",
        event_description=(
            "Transformer differential trip"
        ),
        through_fault_context={
            "upstream_protection_operated": True,
            "downstream_protection_operated": True,
            "transformer_breakers_opened": True,
            "high_through_fault_current_detected": True,
        },
    )

    context = request.through_fault_context

    assert context is not None
    assert context.upstream_protection_operated is True
    assert context.downstream_protection_operated is True
    assert context.transformer_breakers_opened is True
    assert context.high_through_fault_current_detected is True
    assert context.shadow_only is True
    assert context.affects_reasoning is False
    assert context.affects_decision is False


def test_through_fault_context_is_optional():
    request = TransformerDifferentialTripRequest(
        asset_id="T1",
        event_description=(
            "Transformer differential trip"
        ),
    )

    assert request.through_fault_context is None