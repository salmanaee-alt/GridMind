from __future__ import annotations

from app.transformer.physics_contracts import (
    DifferentialCurrentResult,
    HarmonicPhysicsValidity,
    HarmonicRestraintEvaluation,
    DifferentialCharacteristicEvaluation,
)
from app.transformer.physics_observation import (
    PhysicsObservation,
)

from app.transformer.ct_saturation_evaluator import (
    CTSaturationEvaluation,
)

from app.transformer.external_fault_discrimination import (
    ExternalFaultDiscriminationEvaluation,
)
from app.transformer.through_fault_evaluator import (
    ThroughFaultEvaluation,
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


def build_differential_characteristic_observation(
    *,
    result: DifferentialCharacteristicEvaluation,
) -> PhysicsObservation:
    return PhysicsObservation(
        observation_type="differential_characteristic",
        validity_status="valid",
        data={
            "phase_a_operate":
                result.phase_a_operate,
            "phase_b_operate":
                result.phase_b_operate,
            "phase_c_operate":
                result.phase_c_operate,
            "phase_a_threshold_a":
                result.phase_a_threshold_a,
            "phase_b_threshold_a":
                result.phase_b_threshold_a,
            "phase_c_threshold_a":
                result.phase_c_threshold_a,
            "affects_decision":
                result.affects_decision,
        },
        provenance={
            "calculation":
                "differential_characteristic",
            "algorithm_version":
                "v0.40",
            "formulae": {
                "operate_threshold":
                    "pickup + slope * restraint",
                "operate":
                    "Idiff >= operate_threshold",
            },
            "inputs": [
                "differential_current",
                "pickup_a",
                "slope",
            ],
        },
    )


def build_ct_saturation_observation(
    *,
    result: CTSaturationEvaluation,
) -> PhysicsObservation:
    return PhysicsObservation(
        observation_type="ct_saturation_evaluation",
        validity_status="valid",
        data={
            "status": result.status,
            "confirmed": result.confirmed,
            "shadow_only": result.shadow_only,
            "affects_reasoning": (
                result.affects_reasoning
            ),
            "affects_decision": (
                result.affects_decision
            ),
        },
        provenance={
            "calculation":
                "ct_saturation_evaluation",
            "algorithm_version":
                "v0.41",
            "inputs": [
                "waveform_asymmetry_detected",
                "secondary_current_distortion_detected",
                "high_through_fault_current_detected",
            ],
        },
    )


def build_external_fault_discrimination_observation(
    *,
    result: ExternalFaultDiscriminationEvaluation,
) -> PhysicsObservation:
    return PhysicsObservation(
        observation_type=(
            "external_fault_discrimination"
        ),
        validity_status="valid",
        data={
            "status": result.status,
            "confirmed": result.confirmed,
            "shadow_only": result.shadow_only,
            "affects_reasoning": (
                result.affects_reasoning
            ),
            "affects_decision": (
                result.affects_decision
            ),
        },
        provenance={
            "calculation":
                "external_fault_discrimination",
            "algorithm_version":
                "v0.42",
            "inputs": [
                "differential_operating_region",
                "ct_saturation_status",
            ],
        },
    )


def build_through_fault_observation(
    *,
    result: ThroughFaultEvaluation,
) -> PhysicsObservation:
    return PhysicsObservation(
        observation_type="through_fault_evaluation",
        validity_status="valid",
        data={
            "status": result.status,
            "confirmed": result.confirmed,
            "shadow_only": result.shadow_only,
            "affects_reasoning": result.affects_reasoning,
            "affects_decision": result.affects_decision,
        },
        provenance={
            "calculation": "through_fault_evaluation",
            "algorithm_version": "v0.43",
            "inputs": [
                "upstream_protection_operated",
                "downstream_protection_operated",
                "transformer_breakers_opened",
                "high_through_fault_current_detected",
            ],
        },
    )