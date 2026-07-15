from copy import deepcopy

from fastapi.testclient import TestClient

from app.brain.engineering_brain import EngineeringBrain
from app.brain.engineering_session import EngineeringSession
from app.knowledge.bootstrap import build_default_registry
from app.knowledge.context_builder import build_knowledge_context
from app.main import app


client = TestClient(app)


def build_test_session() -> EngineeringSession:
    session = EngineeringSession(
        title="Knowledge shadow regression session",
        metadata={
            "engineering_role": "Transformer Engineer",
            "event_type": "differential_trip",
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


def test_transformer_api_exposes_knowledge_context_in_session_metadata():
    response = client.post(
        "/transformer/differential-trip",
        json={
            "asset_id": "T1",
            "event_description": "Transformer differential trip",
            "available_data": [
                "Relay event report",
            ],
        },
    )

    assert response.status_code == 200

    metadata = response.json()["session"]["metadata"]

    assert "knowledge_context" in metadata

    context = metadata["knowledge_context"]

    assert context["schema_version"] == "1.0.0"
    assert context["shadow"]["enabled"] is True
    assert context["shadow"]["source"] == "registry"
    assert context["shadow"]["affects_decision"] is False


def test_transformer_api_shadow_contains_default_registry_scope():
    response = client.post(
        "/transformer/differential-trip",
        json={
            "available_data": [
                "Relay event report",
            ],
        },
    )

    assert response.status_code == 200

    knowledge = response.json()["session"]["metadata"][
        "knowledge_context"
    ]["shadow"]["knowledge"]

    registry = build_default_registry()

    assert tuple(
        item["knowledge_id"]
        for item in knowledge
    ) == tuple(
        item.knowledge_id
        for item in registry.all()
    )

    assert tuple(
        item["version"]
        for item in knowledge
    ) == tuple(
        item.version
        for item in registry.all()
    )

    assert tuple(
        item["status"]
        for item in knowledge
    ) == tuple(
        item.status
        for item in registry.all()
    )


def test_engineering_brain_preserves_knowledge_context_unchanged():
    registry = build_default_registry()
    context = build_knowledge_context(registry)

    session = build_test_session()
    session.metadata["knowledge_context"] = (
        context.model_dump()
    )

    context_before = deepcopy(
        session.metadata["knowledge_context"]
    )

    completed = EngineeringBrain().run(session)

    assert completed.metadata["knowledge_context"] == (
        context_before
    )


def test_knowledge_context_does_not_change_brain_outputs():
    without_context = build_test_session()
    with_context = build_test_session()

    context = build_knowledge_context(
        build_default_registry()
    )
    with_context.metadata["knowledge_context"] = (
        context.model_dump()
    )

    completed_without = EngineeringBrain().run(
        without_context
    )
    completed_with = EngineeringBrain().run(
        with_context
    )

    assert completed_with.hypotheses == (
        completed_without.hypotheses
    )
    assert completed_with.decisions == (
        completed_without.decisions
    )
    assert completed_with.reports == (
        completed_without.reports
    )
    assert completed_with.reasoning_steps == (
        completed_without.reasoning_steps
    )


def test_knowledge_context_is_serialized_with_session_metadata():
    session = build_test_session()
    context = build_knowledge_context(
        build_default_registry()
    )

    session.metadata["knowledge_context"] = (
        context.model_dump()
    )

    serialized = session.to_dict()

    assert serialized["metadata"]["knowledge_context"] == (
        context.model_dump()
    )
