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
    