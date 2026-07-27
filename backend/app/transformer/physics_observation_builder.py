from __future__ import annotations

from app.transformer.physics_contracts import (
    DifferentialCurrentResult,
    HarmonicPhysicsValidity,
    HarmonicRestraintEvaluation,
)
from app.transformer.physics_observation import (
    PhysicsObservation,
)


def build_differential_current_observation(
    *,
    result: DifferentialCurrentResult,
) -> PhysicsObservation:
    return PhysicsObservation(
        observation_type="differential_current",
        validity_status="valid",
        data={
            "phase_a_diff_a": result.phase_a_diff_a,
            "phase_b_diff_a": result.phase_b_diff_a,
            "phase_c_diff_a": result.phase_c_diff_a,
            "phase_a_restraint_a": (
                result.phase_a_restraint_a
            ),
            "phase_b_restraint_a": (
                result.phase_b_restraint_a
            ),
            "phase_c_restraint_a": (
                result.phase_c_restraint_a
            ),
        },
    )


def build_harmonic_restraint_observation(
    *,
    result: HarmonicRestraintEvaluation,
    validity: HarmonicPhysicsValidity,
) -> PhysicsObservation:
    return PhysicsObservation(
        observation_type="harmonic_restraint",
        validity_status=validity.status,
        data={
            "second_harmonic_restraint": (
                result.second_harmonic_restraint
            ),
            "fifth_harmonic_restraint": (
                result.fifth_harmonic_restraint
            ),
            "any_harmonic_restraint": (
                result.any_harmonic_restraint
            ),
            "ratios_defined": result.ratios_defined,
            "validity_reason": validity.reason,
        },
    )
