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
        provenance={
            "calculation": "differential_current",
            "algorithm_version": "v0.39",
            "formulae": {
                "phase_a_diff_a": (
                    "abs(hv_referred.phase_a - "
                    "lv_referred.phase_a)"
                ),
                "phase_b_diff_a": (
                    "abs(hv_referred.phase_b - "
                    "lv_referred.phase_b)"
                ),
                "phase_c_diff_a": (
                    "abs(hv_referred.phase_c - "
                    "lv_referred.phase_c)"
                ),
                "phase_a_restraint_a": (
                    "(hv_referred.phase_a + "
                    "lv_referred.phase_a) / 2"
                ),
                "phase_b_restraint_a": (
                    "(hv_referred.phase_b + "
                    "lv_referred.phase_b) / 2"
                ),
                "phase_c_restraint_a": (
                    "(hv_referred.phase_c + "
                    "lv_referred.phase_c) / 2"
                ),
            },
            "inputs": [
                "hv_currents",
                "lv_currents",
                "hv_ct_ratio",
                "lv_ct_ratio",
                "voltage_side_referencing",
                "vector_group_compensation",
            ],
        }
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
        provenance={
            "calculation": "harmonic_restraint",
            "algorithm_version": "v0.39",
            "formulae": {
                "second_harmonic_restraint": (
                    "second_harmonic_ratio >= "
                    "second_harmonic_threshold"
                ),
                "fifth_harmonic_restraint": (
                    "fifth_harmonic_ratio >= "
                    "fifth_harmonic_threshold"
                ),
            },
            "inputs": [
                "fundamental_current",
                "second_harmonic",
                "fifth_harmonic",
            ],
        }
    )
