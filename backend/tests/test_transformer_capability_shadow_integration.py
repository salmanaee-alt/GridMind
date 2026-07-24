from copy import deepcopy

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def invoke_transformer_api(
    *,
    available_data: list[str] | None = None,
):
    response = client.post(
        "/transformer/differential-trip",
        json={
            "available_data": (
                available_data
                if available_data is not None
                else [
                    "Relay event report",
                ]
            ),
        },
    )

    assert response.status_code == 200

    return response.json()["session"]


def test_transformer_session_exposes_capability_execution():
    session = invoke_transformer_api()
    metadata = session["metadata"]

    assert "capability_executions" in metadata
    assert isinstance(
        metadata["capability_executions"],
        list,
    )
    assert len(
        metadata["capability_executions"]
    ) == 4

    capability_ids = [
        execution["capability_id"]
        for execution in metadata["capability_executions"]
    ]

    assert capability_ids == [
        "CAP-KNOWLEDGE-0001",
        "CAP-KNOWLEDGERELEVANCE-0001",
        "CAP-EVIDENCEINTERP-0001",
        "CAP-TRACEABLECTX-0001",
    ]


def test_capability_execution_summary_is_shadow_only():
    session = invoke_transformer_api()

    execution = session["metadata"][
        "capability_executions"
    ][0]

    assert execution["capability_id"] == (
        "CAP-KNOWLEDGE-0001"
    )
    assert execution["status"] == "success"
    assert execution["execution_mode"] == "shadow"
    assert execution["affects_decision"] is False
    assert execution["duration_ms"] >= 0
    assert execution["error"] is None


def test_capability_execution_reports_candidate_count():
    session = invoke_transformer_api()

    execution = session["metadata"][
        "capability_executions"
    ][0]

    assert execution["candidate_count"] == 3


def test_knowledge_relevance_execution_is_shadow_only():
    session = invoke_transformer_api()

    execution = session["metadata"][
        "capability_executions"
    ][1]

    assert execution["capability_id"] == (
        "CAP-KNOWLEDGERELEVANCE-0001"
    )
    assert execution["status"] == "success"
    assert execution["execution_mode"] == "shadow"
    assert execution["affects_decision"] is False
    assert execution["duration_ms"] >= 0
    assert execution["selected_count"] >= 0
    assert execution["ignored_count"] >= 0
    assert execution["error"] is None


def test_capability_output_does_not_leak_into_decisions():
    session = invoke_transformer_api()

    for decision in session["decisions"]:
        assert "capability_executions" not in decision
        assert "knowledge_candidate_result" not in decision
        assert "knowledge_relevance_result" not in decision
        assert "candidate_count" not in decision
        assert "selected_count" not in decision
        assert "ignored_count" not in decision


def test_capability_output_does_not_leak_into_reports():
    session = invoke_transformer_api()

    for report in session["reports"]:
        assert "capability_executions" not in report
        assert "knowledge_candidate_result" not in report
        assert "knowledge_relevance_result" not in report
        assert "candidate_count" not in report
        assert "selected_count" not in report
        assert "ignored_count" not in report


def test_capability_execution_does_not_mutate_engineering_outputs():
    first = invoke_transformer_api(
        available_data=[
            "Relay event report",
        ],
    )
    second = invoke_transformer_api(
        available_data=[
            "Relay event report",
        ],
    )

    first_without_metadata = deepcopy(first)
    second_without_metadata = deepcopy(second)

    first_without_metadata["metadata"].pop(
        "capability_executions",
        None,
    )
    second_without_metadata["metadata"].pop(
        "capability_executions",
        None,
    )

    assert first_without_metadata["hypotheses"] == (
        second_without_metadata["hypotheses"]
    )
    assert first_without_metadata["decisions"] == (
        second_without_metadata["decisions"]
    )
    assert first_without_metadata["reports"] == (
        second_without_metadata["reports"]
    )
    assert first_without_metadata["reasoning_steps"] == (
        second_without_metadata["reasoning_steps"]
    )


def test_capability_execution_remains_separate_from_knowledge_audit():
    session = invoke_transformer_api()
    metadata = session["metadata"]

    capability_execution = metadata[
        "capability_executions"
    ][0]
    knowledge_audit = metadata[
        "knowledge_audit"
    ]

    assert capability_execution is not knowledge_audit
    assert capability_execution[
        "capability_id"
    ] == "CAP-KNOWLEDGE-0001"
    assert knowledge_audit[
        "registry_source"
    ] == "default_registry"


def test_capability_failure_does_not_block_engineering_analysis(
    monkeypatch,
):
    from app.capabilities.knowledge import (
        KnowledgeCandidateCapability,
    )

    def fail_execute(
        self,
        request,
    ):
        raise RuntimeError(
            "simulated shadow capability failure"
        )

    monkeypatch.setattr(
        KnowledgeCandidateCapability,
        "execute",
        fail_execute,
    )

    session = invoke_transformer_api()

    execution = session["metadata"][
        "capability_executions"
    ][0]

    assert execution["status"] == "error"
    assert execution["affects_decision"] is False
    assert execution["error"]["error_type"] == (
        "execution_error"
    )

    assert session["hypotheses"]
    assert session["decisions"]
    assert session["reports"]


def test_traceable_context_exposes_coverage_audit_without_decision_leak():
    session = invoke_transformer_api()

    execution = session["metadata"][
        "capability_executions"
    ][3]

    assert execution["capability_id"] == (
        "CAP-TRACEABLECTX-0001"
    )
    assert execution["status"] == "success"
    assert execution["execution_mode"] == "shadow"
    assert execution["affects_decision"] is False

    assert execution[
        "interpreted_evidence_count"
    ] >= 0

    assert execution[
        "traced_evidence_count"
    ] >= 0

    assert execution[
        "untraced_evidence_count"
    ] >= 0

    assert 0.0 <= execution[
        "traceability_ratio"
    ] <= 1.0

    assert (
        execution["traced_evidence_count"]
        + execution["untraced_evidence_count"]
        == execution["interpreted_evidence_count"]
    )

    for decision in session["decisions"]:
        assert "traceability_ratio" not in decision
        assert "traced_evidence_count" not in decision
        assert "untraced_evidence_count" not in decision
        assert "traceable_engineering_context" not in decision

    for report in session["reports"]:
        assert "traceability_ratio" not in report
        assert "traced_evidence_count" not in report
        assert "untraced_evidence_count" not in report
        assert "traceable_engineering_context" not in report