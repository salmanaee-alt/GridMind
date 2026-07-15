from copy import deepcopy

from fastapi.testclient import TestClient

from app.brain.engineering_brain import EngineeringBrain
from app.brain.engineering_session import EngineeringSession
from app.knowledge.bootstrap import build_default_registry
from app.knowledge.context_builder import build_knowledge_context
from app.main import app


client = TestClient(app)


def build_audited_session() -> EngineeringSession:
    context = build_knowledge_context(
        build_default_registry()
    )

    session = EngineeringSession(
        title="Knowledge audit regression session",
        metadata={
            "engineering_role": "Transformer Engineer",
            "event_type": "differential_trip",
            "knowledge_context": context.model_dump(),
            "knowledge_audit": {
                "schema_version": context.schema_version,
                "registry_source": "default_registry",
                "knowledge_count": len(
                    context.shadow.knowledge
                ),
                "knowledge_ids": [
                    item.knowledge_id
                    for item in context.shadow.knowledge
                ],
                "shadow_mode": context.shadow.enabled,
                "affects_decision": (
                    context.shadow.affects_decision
                ),
            },
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


def test_transformer_api_exposes_knowledge_audit():
    response = client.post(
        "/transformer/differential-trip",
        json={
            "available_data": [
                "Relay event report",
            ],
        },
    )

    assert response.status_code == 200

    metadata = response.json()["session"]["metadata"]

    assert "knowledge_audit" in metadata


def test_knowledge_audit_matches_context_schema_version():
    response = client.post(
        "/transformer/differential-trip",
        json={},
    )

    metadata = response.json()["session"]["metadata"]
    audit = metadata["knowledge_audit"]
    context = metadata["knowledge_context"]

    assert audit["schema_version"] == (
        context["schema_version"]
    )


def test_knowledge_audit_uses_default_registry_source():
    response = client.post(
        "/transformer/differential-trip",
        json={},
    )

    audit = response.json()["session"]["metadata"][
        "knowledge_audit"
    ]

    assert audit["registry_source"] == "default_registry"


def test_knowledge_audit_count_and_ids_match_context():
    response = client.post(
        "/transformer/differential-trip",
        json={},
    )

    metadata = response.json()["session"]["metadata"]
    audit = metadata["knowledge_audit"]
    knowledge = metadata["knowledge_context"][
        "shadow"
    ]["knowledge"]

    expected_ids = [
        item["knowledge_id"]
        for item in knowledge
    ]

    assert audit["knowledge_count"] == len(knowledge)
    assert audit["knowledge_ids"] == expected_ids


def test_knowledge_audit_remains_shadow_only():
    response = client.post(
        "/transformer/differential-trip",
        json={},
    )

    audit = response.json()["session"]["metadata"][
        "knowledge_audit"
    ]

    assert audit["shadow_mode"] is True
    assert audit["affects_decision"] is False


def test_knowledge_audit_survives_serialization():
    session = build_audited_session()

    serialized = session.to_dict()

    assert serialized["metadata"]["knowledge_audit"] == (
        session.metadata["knowledge_audit"]
    )


def test_brain_preserves_knowledge_audit_unchanged():
    session = build_audited_session()
    before = deepcopy(
        session.metadata["knowledge_audit"]
    )

    completed = EngineeringBrain().run(session)

    assert completed.metadata["knowledge_audit"] == before


def test_knowledge_audit_does_not_change_brain_outputs():
    without_audit = build_audited_session()
    with_audit = build_audited_session()

    del without_audit.metadata["knowledge_audit"]

    completed_without = EngineeringBrain().run(
        without_audit
    )
    completed_with = EngineeringBrain().run(
        with_audit
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


def test_knowledge_audit_does_not_leak_into_decision_or_report():
    session = build_audited_session()

    completed = EngineeringBrain().run(session)

    assert "knowledge_audit" not in completed.decisions[-1]
    assert "knowledge_audit" not in completed.reports[-1]
