import pytest


from app.transformer.physics import (
    calculate_differential_and_restraint_currents,
    differential_currents_are_comparable,
    evaluate_differential_characteristic,
    normalize_current_to_ct_secondary,
    refer_current_to_voltage_side,
    calculate_harmonic_ratios,
    evaluate_harmonic_restraint,
    evaluate_harmonic_physics_validity,
    summarize_differential_operating_region
)

from app.transformer.physics_contracts import (
    CTRatio,
    DifferentialCharacteristicSettings,
    ThreePhaseCurrentMeasurement,
    TransformerDifferentialPhysicsContext,
    HarmonicCurrentMeasurement,
    HarmonicRestraintSettings,
    DifferentialCharacteristicEvaluation,
)


def test_ct_secondary_normalization_is_correct():
    currents = ThreePhaseCurrentMeasurement(
        phase_a=1200.0,
        phase_b=600.0,
        phase_c=300.0,
    )

    ct_ratio = CTRatio(
        primary_a=1200.0,
        secondary_a=1.0,
    )

    normalized = normalize_current_to_ct_secondary(
        currents=currents,
        ct_ratio=ct_ratio,
    )

    assert normalized.phase_a == 1.0
    assert normalized.phase_b == 0.5
    assert normalized.phase_c == 0.25


def test_ct_secondary_normalization_supports_five_amp_ct():
    currents = ThreePhaseCurrentMeasurement(
        phase_a=1200.0,
        phase_b=1200.0,
        phase_c=1200.0,
    )

    ct_ratio = CTRatio(
        primary_a=1200.0,
        secondary_a=5.0,
    )

    normalized = normalize_current_to_ct_secondary(
        currents=currents,
        ct_ratio=ct_ratio,
    )

    assert normalized.phase_a == 5.0
    assert normalized.phase_b == 5.0
    assert normalized.phase_c == 5.0


def test_lv_current_can_be_referred_to_hv_side():
    currents = ThreePhaseCurrentMeasurement(
        phase_a=1000.0,
        phase_b=500.0,
        phase_c=250.0,
    )

    referred = refer_current_to_voltage_side(
        currents=currents,
        from_voltage_kv=13.8,
        to_voltage_kv=230.0,
    )

    assert referred.phase_a == pytest.approx(60.0)
    assert referred.phase_b == pytest.approx(30.0)
    assert referred.phase_c == pytest.approx(15.0)


def test_hv_current_can_be_referred_to_lv_side():
    currents = ThreePhaseCurrentMeasurement(
        phase_a=60.0,
        phase_b=30.0,
        phase_c=15.0,
    )

    referred = refer_current_to_voltage_side(
        currents=currents,
        from_voltage_kv=230.0,
        to_voltage_kv=13.8,
    )

    assert referred.phase_a == pytest.approx(1000.0)
    assert referred.phase_b == pytest.approx(500.0)
    assert referred.phase_c == pytest.approx(250.0)


def test_current_referencing_rejects_invalid_voltage():
    currents = ThreePhaseCurrentMeasurement(
        phase_a=100.0,
        phase_b=100.0,
        phase_c=100.0,
    )

    with pytest.raises(
        ValueError,
        match="from_voltage_kv",
    ):
        refer_current_to_voltage_side(
            currents=currents,
            from_voltage_kv=0.0,
            to_voltage_kv=230.0,
        )


def test_differential_comparison_is_blocked_when_vector_group_unknown():
    context = TransformerDifferentialPhysicsContext()

    assert (
        differential_currents_are_comparable(
            context=context
        )
        is False
    )


def test_differential_comparison_is_blocked_without_compensation():
    context = TransformerDifferentialPhysicsContext(
        vector_group="Dyn11",
        vector_group_compensation_applied=False,
    )

    assert (
        differential_currents_are_comparable(
            context=context
        )
        is False
    )


def test_differential_comparison_allowed_after_known_compensation():
    context = TransformerDifferentialPhysicsContext(
        vector_group="Dyn11",
        vector_group_compensation_applied=True,
    )

    assert (
        differential_currents_are_comparable(
            context=context
        )
        is True
    )


def test_differential_and_restraint_currents_are_calculated():
    context = TransformerDifferentialPhysicsContext(
        vector_group="Dyn11",
        vector_group_compensation_applied=True,
    )

    hv = ThreePhaseCurrentMeasurement(
        phase_a=100.0,
        phase_b=100.0,
        phase_c=100.0,
    )

    lv_referred = ThreePhaseCurrentMeasurement(
        phase_a=95.0,
        phase_b=105.0,
        phase_c=100.0,
    )

    result = calculate_differential_and_restraint_currents(
        hv_currents=hv,
        lv_currents_referred_to_hv=lv_referred,
        context=context,
    )

    assert result.phase_a_diff_a == 5.0
    assert result.phase_b_diff_a == 5.0
    assert result.phase_c_diff_a == 0.0

    assert result.phase_a_restraint_a == 97.5
    assert result.phase_b_restraint_a == 102.5
    assert result.phase_c_restraint_a == 100.0

    assert result.affects_decision is False


def test_differential_calculation_is_blocked_before_compensation():
    context = TransformerDifferentialPhysicsContext(
        vector_group="Dyn11",
        vector_group_compensation_applied=False,
    )

    currents = ThreePhaseCurrentMeasurement(
        phase_a=100.0,
        phase_b=100.0,
        phase_c=100.0,
    )

    with pytest.raises(
        ValueError,
        match="not physically comparable",
    ):
        calculate_differential_and_restraint_currents(
            hv_currents=currents,
            lv_currents_referred_to_hv=currents,
            context=context,
        )


def test_differential_characteristic_operates_above_threshold():
    context = TransformerDifferentialPhysicsContext(
        vector_group="Dyn11",
        vector_group_compensation_applied=True,
    )

    hv = ThreePhaseCurrentMeasurement(
        phase_a=100.0,
        phase_b=100.0,
        phase_c=100.0,
    )

    lv = ThreePhaseCurrentMeasurement(
        phase_a=70.0,
        phase_b=100.0,
        phase_c=100.0,
    )

    currents = calculate_differential_and_restraint_currents(
        hv_currents=hv,
        lv_currents_referred_to_hv=lv,
        context=context,
    )

    settings = DifferentialCharacteristicSettings(
        pickup_a=5.0,
        slope=0.20,
    )

    result = evaluate_differential_characteristic(
        currents=currents,
        settings=settings,
    )

    assert result.phase_a_operate is True
    assert result.phase_b_operate is False
    assert result.phase_c_operate is False
    assert result.affects_decision is False


def test_differential_characteristic_restrains_below_threshold():
    context = TransformerDifferentialPhysicsContext(
        vector_group="Dyn11",
        vector_group_compensation_applied=True,
    )

    hv = ThreePhaseCurrentMeasurement(
        phase_a=100.0,
        phase_b=100.0,
        phase_c=100.0,
    )

    lv = ThreePhaseCurrentMeasurement(
        phase_a=95.0,
        phase_b=95.0,
        phase_c=95.0,
    )

    currents = calculate_differential_and_restraint_currents(
        hv_currents=hv,
        lv_currents_referred_to_hv=lv,
        context=context,
    )

    settings = DifferentialCharacteristicSettings(
        pickup_a=5.0,
        slope=0.20,
    )

    result = evaluate_differential_characteristic(
        currents=currents,
        settings=settings,
    )

    assert result.phase_a_operate is False
    assert result.phase_b_operate is False
    assert result.phase_c_operate is False


def test_differential_operating_region_reports_operating_phases():
    context = TransformerDifferentialPhysicsContext(
        vector_group="Dyn11",
        vector_group_compensation_applied=True,
    )

    hv = ThreePhaseCurrentMeasurement(
        phase_a=100.0,
        phase_b=100.0,
        phase_c=100.0,
    )

    lv = ThreePhaseCurrentMeasurement(
        phase_a=70.0,
        phase_b=100.0,
        phase_c=100.0,
    )

    currents = calculate_differential_and_restraint_currents(
        hv_currents=hv,
        lv_currents_referred_to_hv=lv,
        context=context,
    )

    characteristic = evaluate_differential_characteristic(
        currents=currents,
        settings=DifferentialCharacteristicSettings(
            pickup_a=5.0,
            slope=0.20,
        ),
    )

    summary = summarize_differential_operating_region(
        characteristic
    )

    assert summary.any_phase_operate is True
    assert summary.operating_phases == ("A",)
    assert summary.shadow_only is True
    assert summary.affects_reasoning is False
    assert summary.affects_decision is False


def test_differential_operating_region_reports_no_operation():
    characteristic = DifferentialCharacteristicEvaluation(
        phase_a_operate=False,
        phase_b_operate=False,
        phase_c_operate=False,
        phase_a_threshold_a=10.0,
        phase_b_threshold_a=10.0,
        phase_c_threshold_a=10.0,
    )

    summary = summarize_differential_operating_region(
        characteristic
    )

    assert summary.any_phase_operate is False
    assert summary.operating_phases == ()
    assert summary.shadow_only is True
    assert summary.affects_reasoning is False
    assert summary.affects_decision is False


def test_harmonic_ratios_are_calculated():
    measurement = HarmonicCurrentMeasurement(
        fundamental_a=100.0,
        second_harmonic_a=20.0,
        fifth_harmonic_a=5.0,
    )

    result = calculate_harmonic_ratios(
        measurement=measurement
    )

    assert result["second_harmonic_percent"] == 20.0
    assert result["fifth_harmonic_percent"] == 5.0
    assert result["ratios_defined"] is True
    assert result["affects_decision"] is False


def test_harmonic_ratios_are_undefined_when_fundamental_is_zero():
    measurement = HarmonicCurrentMeasurement(
        fundamental_a=0.0,
        second_harmonic_a=10.0,
        fifth_harmonic_a=5.0,
    )

    result = calculate_harmonic_ratios(
        measurement=measurement
    )

    assert result["second_harmonic_percent"] is None
    assert result["fifth_harmonic_percent"] is None
    assert result["ratios_defined"] is False
    assert result["affects_decision"] is False


def test_second_harmonic_restraint_is_detected():
    measurement = HarmonicCurrentMeasurement(
        fundamental_a=100.0,
        second_harmonic_a=25.0,
        fifth_harmonic_a=2.0,
    )

    settings = HarmonicRestraintSettings(
        second_harmonic_threshold_percent=15.0,
        fifth_harmonic_threshold_percent=20.0,
    )

    result = evaluate_harmonic_restraint(
        measurement=measurement,
        settings=settings,
    )

    assert result.second_harmonic_restraint is True
    assert result.fifth_harmonic_restraint is False
    assert result.any_harmonic_restraint is True
    assert result.affects_decision is False


def test_fifth_harmonic_restraint_is_detected():
    measurement = HarmonicCurrentMeasurement(
        fundamental_a=100.0,
        second_harmonic_a=5.0,
        fifth_harmonic_a=25.0,
    )

    settings = HarmonicRestraintSettings(
        second_harmonic_threshold_percent=15.0,
        fifth_harmonic_threshold_percent=20.0,
    )

    result = evaluate_harmonic_restraint(
        measurement=measurement,
        settings=settings,
    )

    assert result.second_harmonic_restraint is False
    assert result.fifth_harmonic_restraint is True
    assert result.any_harmonic_restraint is True


def test_harmonic_restraint_is_false_when_below_thresholds():
    measurement = HarmonicCurrentMeasurement(
        fundamental_a=100.0,
        second_harmonic_a=5.0,
        fifth_harmonic_a=5.0,
    )

    settings = HarmonicRestraintSettings(
        second_harmonic_threshold_percent=15.0,
        fifth_harmonic_threshold_percent=20.0,
    )

    result = evaluate_harmonic_restraint(
        measurement=measurement,
        settings=settings,
    )

    assert result.any_harmonic_restraint is False


def test_harmonic_restraint_is_not_evaluated_when_ratios_undefined():
    measurement = HarmonicCurrentMeasurement(
        fundamental_a=0.0,
        second_harmonic_a=20.0,
        fifth_harmonic_a=20.0,
    )

    settings = HarmonicRestraintSettings(
        second_harmonic_threshold_percent=15.0,
        fifth_harmonic_threshold_percent=20.0,
    )

    result = evaluate_harmonic_restraint(
        measurement=measurement,
        settings=settings,
    )

    assert result.ratios_defined is False
    assert result.any_harmonic_restraint is False


def test_harmonic_physics_validity_is_valid_with_fundamental():
    measurement = HarmonicCurrentMeasurement(
        fundamental_a=100.0,
        second_harmonic_a=20.0,
    )

    result = evaluate_harmonic_physics_validity(
        measurement=measurement
    )

    assert result.status == "valid"
    assert result.affects_decision is False


def test_harmonic_physics_validity_is_unavailable_without_measurement():
    result = evaluate_harmonic_physics_validity(
        measurement=None
    )

    assert result.status == "unavailable"
    assert result.affects_decision is False


def test_harmonic_physics_validity_is_indeterminate_with_zero_fundamental():
    measurement = HarmonicCurrentMeasurement(
        fundamental_a=0.0,
        second_harmonic_a=20.0,
    )

    result = evaluate_harmonic_physics_validity(
        measurement=measurement
    )

    assert result.status == "indeterminate"
    assert result.affects_decision is False
    