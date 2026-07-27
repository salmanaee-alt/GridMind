from app.transformer.physics_contracts import (
    DifferentialCurrentResult,
    HarmonicPhysicsValidity,
    HarmonicRestraintEvaluation,
)
from app.transformer.physics_observation_builder import (
    build_differential_current_observation,
    build_harmonic_restraint_observation,
)


def test_differential_result_builds_shadow_observation():
    result = DifferentialCurrentResult(
        phase_a_diff_a=5.0,
        phase_b_diff_a=4.0,
        phase_c_diff_a=3.0,
        phase_a_restraint_a=100.0,
        phase_b_restraint_a=101.0,
        phase_c_restraint_a=99.0,
    )

    observation = build_differential_current_observation(
        result=result
    )

    assert (
        observation.observation_type
        == "differential_current"
    )
    assert observation.validity_status == "valid"
    assert observation.data["phase_a_diff_a"] == 5.0
    assert observation.affects_decision is False


def test_harmonic_result_builds_shadow_observation():
    result = HarmonicRestraintEvaluation(
        second_harmonic_restraint=True,
        fifth_harmonic_restraint=False,
        any_harmonic_restraint=True,
        ratios_defined=True,
    )

    validity = HarmonicPhysicsValidity(
        status="valid",
        reason="Harmonic ratios are available.",
    )

    observation = build_harmonic_restraint_observation(
        result=result,
        validity=validity,
    )

    assert (
        observation.observation_type
        == "harmonic_restraint"
    )
    assert observation.validity_status == "valid"
    assert (
        observation.data["any_harmonic_restraint"]
        is True
    )
    assert observation.affects_confidence is False
    assert observation.affects_ranking is False
    assert observation.affects_decision is False
    