from app.brain.evidence_adapter import (
    physics_observation_to_evidence,
)
from app.brain.evidence_contracts import (
    EvidenceCategory,
    EvidenceValidity,
)
from app.transformer.physics_observation import (
    PhysicsObservation,
)


import pytest


@pytest.mark.parametrize(
    ("validity_status", "expected"),
    [
        ("valid", EvidenceValidity.VALID),
        ("invalid", EvidenceValidity.INVALID),
        ("unknown", EvidenceValidity.UNKNOWN),
        ("unavailable", EvidenceValidity.INSUFFICIENT),
        ("indeterminate", EvidenceValidity.UNKNOWN),
        ("unexpected_status", EvidenceValidity.UNKNOWN),
    ],
)
def test_maps_all_supported_validity_statuses(
    validity_status,
    expected,
):
    observation = PhysicsObservation(
        observation_type="physics",
        validity_status=validity_status,
    )

    evidence = physics_observation_to_evidence(
        observation
    )

    assert evidence.validity == expected


def test_converts_physics_observation_to_engineering_evidence():
    observation = PhysicsObservation(
        observation_type="differential_current",
        validity_status="valid",
        data={
            "phase_a_diff_a": 5.1,
            "phase_a_restraint_a": 102.3,
        },
        provenance={
            "algorithm_version": "v0.39",
        },
    )

    evidence = physics_observation_to_evidence(
        observation
    )

    assert evidence.evidence_id == (
        "physics:differential_current"
    )

    assert evidence.evidence_type == (
        "differential_current"
    )

    assert evidence.category == (
        EvidenceCategory.PHYSICS
    )

    assert evidence.source == (
        "transformer_physics"
    )


def test_transfers_data():
    observation = PhysicsObservation(
        observation_type="harmonic_restraint",
        validity_status="valid",
        data={
            "second_harmonic_restraint": True,
            "fifth_harmonic_restraint": False,
        },
    )

    evidence = physics_observation_to_evidence(
        observation
    )

    assert evidence.value == observation.data


def test_transfers_provenance():
    observation = PhysicsObservation(
        observation_type="harmonic_restraint",
        validity_status="valid",
        provenance={
            "algorithm_version": "v0.39",
            "inputs": [
                "fundamental_current",
                "second_harmonic",
            ],
        },
    )

    evidence = physics_observation_to_evidence(
        observation
    )

    assert evidence.provenance == (
        observation.provenance
    )


def test_maps_validity_status():
    observation = PhysicsObservation(
        observation_type="physics",
        validity_status="valid",
    )

    evidence = physics_observation_to_evidence(
        observation
    )

    assert evidence.validity == (
        EvidenceValidity.VALID
    )


def test_affects_reasoning_remains_false():
    observation = PhysicsObservation(
        observation_type="physics",
    )

    evidence = physics_observation_to_evidence(
        observation
    )

    assert evidence.affects_reasoning is False
