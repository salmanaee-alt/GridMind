import pytest
from pydantic import ValidationError

from app.transformer.physics_contracts import (
    CTRatio,
    ThreePhaseCurrentMeasurement,
    TransformerElectricalMeasurements,
    TransformerDifferentialPhysicsContext,
)


def test_three_phase_current_measurement_accepts_positive_values():
    measurement = ThreePhaseCurrentMeasurement(
        phase_a=100.0,
        phase_b=101.0,
        phase_c=99.0,
    )

    assert measurement.phase_a == 100.0
    assert measurement.phase_b == 101.0
    assert measurement.phase_c == 99.0
    assert measurement.unit == "A"


def test_three_phase_current_measurement_rejects_negative_current():
    with pytest.raises(ValidationError):
        ThreePhaseCurrentMeasurement(
            phase_a=-1.0,
            phase_b=10.0,
            phase_c=10.0,
        )


def test_ct_ratio_property_is_correct():
    ratio = CTRatio(
        primary_a=1200.0,
        secondary_a=1.0,
    )

    assert ratio.ratio == 1200.0


def test_ct_ratio_rejects_zero_secondary():
    with pytest.raises(ValidationError):
        CTRatio(
            primary_a=1200.0,
            secondary_a=0.0,
        )


def test_hv_current_requires_hv_ct_ratio():
    with pytest.raises(
        ValidationError,
        match="hv_ct_ratio is required",
    ):
        TransformerElectricalMeasurements(
            hv_currents=ThreePhaseCurrentMeasurement(
                phase_a=100.0,
                phase_b=100.0,
                phase_c=100.0,
            ),
        )


def test_lv_current_requires_lv_ct_ratio():
    with pytest.raises(
        ValidationError,
        match="lv_ct_ratio is required",
    ):
        TransformerElectricalMeasurements(
            lv_currents=ThreePhaseCurrentMeasurement(
                phase_a=1000.0,
                phase_b=1000.0,
                phase_c=1000.0,
            ),
        )


def test_complete_measurement_contract_is_valid():
    measurements = TransformerElectricalMeasurements(
        hv_currents=ThreePhaseCurrentMeasurement(
            phase_a=100.0,
            phase_b=101.0,
            phase_c=99.0,
        ),
        lv_currents=ThreePhaseCurrentMeasurement(
            phase_a=1670.0,
            phase_b=1680.0,
            phase_c=1660.0,
        ),
        hv_ct_ratio=CTRatio(
            primary_a=200.0,
            secondary_a=1.0,
        ),
        lv_ct_ratio=CTRatio(
            primary_a=2000.0,
            secondary_a=1.0,
        ),
        hv_nominal_voltage_kv=230.0,
        lv_nominal_voltage_kv=13.8,
    )

    assert measurements.hv_nominal_voltage_kv == 230.0
    assert measurements.lv_nominal_voltage_kv == 13.8


def test_vector_group_defaults_to_unknown():
    context = TransformerDifferentialPhysicsContext()

    assert context.vector_group == "unknown"
    assert (
        context.vector_group_compensation_applied
        is False
    )
    assert context.affects_decision is False


def test_known_vector_group_can_declare_compensation():
    context = TransformerDifferentialPhysicsContext(
        vector_group="Dyn11",
        vector_group_compensation_applied=True,
    )

    assert context.vector_group == "Dyn11"
    assert (
        context.vector_group_compensation_applied
        is True
    )


def test_unknown_vector_group_cannot_claim_compensation():
    with pytest.raises(
        ValidationError,
        match="vector-group compensation",
    ):
        TransformerDifferentialPhysicsContext(
            vector_group="unknown",
            vector_group_compensation_applied=True,
        )