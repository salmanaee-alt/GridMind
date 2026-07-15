from copy import deepcopy

from app.brain.engineering_brain import EngineeringBrain
from app.brain.engineering_session import EngineeringSession
from app.knowledge.bootstrap import build_default_registry
from app.knowledge.context_builder import build_knowledge_context


def build_session_with_knowledge_context() -> EngineeringSession:
    context = build_knowledge_context(
        build_default_registry()
    )

    session = EngineeringSession(
        title="Knowledge context persistence contract",
        metadata={
            "engineering_role": "Transformer Engineer",
            "event_type": "differential_trip",
            "knowledge_context": context.model_dump(),
        },
    )

    session.add_observation({
        "available_evidence": [
            "Relay event report",
        ],
        "missing_required_evidence": [
            "COMTRADE waveform",
        ],
        "evidence_metadata": [],
        "dga_status": "not_available",
        "buchholz_alarm": None,
        "oil_temperature_c": None,
        "hv_breaker_status": "unknown",
        "lv_breaker_status": "unknown",
    })

    session.add_hypothesis({
        "hypothesis": "Internal Transformer Fault",
        "confidence": "medium",
        "supporting_evidence": [
            "Relay event report",
        ],
        "missing_evidence": [
            "COMTRADE waveform",
        ],
        "conflicts": [],
        "risk": "high",
        "recommended_next_action": (
            "Review COMTRADE and transformer condition."
        ),
        "why_supported": [
            "Relay event report",
        ],
        "why_not_confirmed": [
            "COMTRADE waveform",
        ],
        "confidence_drivers": [
            "Relay event report",
        ],
        "confidence_limiters": [
            "COMTRADE waveform",
        ],
        "evidence_that_would_change_decision": [
            "COMTRADE waveform",
        ],
    })

    return session


def test_knowledge_context_survives_full_brain_lifecycle():
    session = build_session_with_knowledge_context()
    before = deepcopy(
        session.metadata["knowledge_context"]
    )

    completed = EngineeringBrain().run(session)

    assert completed.metadata["knowledge_context"] == before


def test_brain_preserves_exact_knowledge_context_object():
    session = build_session_with_knowledge_context()
    context_object = session.metadata["knowledge_context"]

    completed = EngineeringBrain().run(session)

    assert completed.metadata["knowledge_context"] is (
        context_object
    )


def test_knowledge_context_contract_fields_remain_unchanged():
    session = build_session_with_knowledge_context()
    before = deepcopy(
        session.metadata["knowledge_context"]
    )

    completed = EngineeringBrain().run(session)
    after = completed.metadata["knowledge_context"]

    assert after["schema_version"] == before["schema_version"]
    assert after["shadow"]["enabled"] == (
        before["shadow"]["enabled"]
    )
    assert after["shadow"]["source"] == (
        before["shadow"]["source"]
    )
    assert after["shadow"]["affects_decision"] is False
    assert after["shadow"]["knowledge"] == (
        before["shadow"]["knowledge"]
    )


def test_knowledge_reference_order_and_values_persist():
    session = build_session_with_knowledge_context()

    before = deepcopy(
        session.metadata["knowledge_context"][
            "shadow"
        ]["knowledge"]
    )

    completed = EngineeringBrain().run(session)

    after = completed.metadata["knowledge_context"][
        "shadow"
    ]["knowledge"]

    assert after == before

    assert [
        item["knowledge_id"]
        for item in after
    ] == [
        item["knowledge_id"]
        for item in before
    ]

    assert [
        item["version"]
        for item in after
    ] == [
        item["version"]
        for item in before
    ]

    assert [
        item["status"]
        for item in after
    ] == [
        item["status"]
        for item in before
    ]


def test_session_serialization_preserves_knowledge_context():
    session = build_session_with_knowledge_context()
    completed = EngineeringBrain().run(session)

    serialized = completed.to_dict()

    assert serialized["metadata"]["knowledge_context"] == (
        completed.metadata["knowledge_context"]
    )


def test_serialized_context_is_independent_from_session_state():
    session = build_session_with_knowledge_context()
    completed = EngineeringBrain().run(session)

    original = deepcopy(
        completed.metadata["knowledge_context"]
    )
    serialized = completed.to_dict()

    serialized["metadata"]["knowledge_context"][
        "shadow"
    ]["enabled"] = False

    assert completed.metadata["knowledge_context"] == original


def test_completed_session_guard_preserves_knowledge_context():
    session = build_session_with_knowledge_context()
    brain = EngineeringBrain()

    completed = brain.run(session)
    context_object = completed.metadata["knowledge_context"]
    before = deepcopy(context_object)

    rerun = brain.run(completed)

    assert rerun.metadata["knowledge_context"] is context_object
    assert rerun.metadata["knowledge_context"] == before


def test_knowledge_context_remains_shadow_only():
    session = build_session_with_knowledge_context()
    completed = EngineeringBrain().run(session)

    context = completed.metadata["knowledge_context"]

    assert context["shadow"]["enabled"] is True
    assert context["shadow"]["affects_decision"] is False

    assert "knowledge_context" not in completed.decisions[-1]
    assert "knowledge_context" not in completed.reports[-1]
