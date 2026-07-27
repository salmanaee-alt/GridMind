from app.brain.engineering_session import EngineeringSession
from app.transformer.physics_observation import PhysicsObservation


def test_physics_observation_is_shadow_only():
    observation = PhysicsObservation(
        observation_type="differential_current",
        data={
            "phase_a_diff_a": 5.0,
            "phase_a_restraint_a": 97.5,
        },
        validity_status="valid",
    )

    assert observation.source == "transformer_physics"
    assert observation.affects_confidence is False
    assert observation.affects_ranking is False
    assert observation.affects_decision is False


def test_physics_observation_can_be_added_to_engineering_session():
    session = EngineeringSession(
        title="Transformer differential investigation"
    )

    observation = PhysicsObservation(
        observation_type="harmonic_restraint",
        data={
            "second_harmonic_percent": 20.0,
            "any_harmonic_restraint": True,
        },
        validity_status="valid",
    )

    session.add_observation(
        observation.model_dump()
    )

    assert len(session.observations) == 1

    stored = session.observations[0]

    assert stored["observation_type"] == "harmonic_restraint"
    assert stored["source"] == "transformer_physics"
    assert stored["affects_decision"] is False


def test_physics_observation_is_serialized_with_session():
    session = EngineeringSession(
        title="Transformer differential investigation"
    )

    observation = PhysicsObservation(
        observation_type="physics_validity",
        data={
            "status": "valid",
        },
        validity_status="valid",
    )

    session.add_observation(
        observation.model_dump()
    )

    serialized = session.to_dict()

    assert (
        serialized["observations"][0]["observation_type"]
        == "physics_validity"
    )

    assert (
        serialized["observations"][0]["affects_decision"]
        is False
    )
    