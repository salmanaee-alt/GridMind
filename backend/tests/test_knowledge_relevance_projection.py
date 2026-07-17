from app.capabilities.knowledge_relevance.projection import (
    project_knowledge_candidate,
)
from app.knowledge.transformer import (
    INTERNAL_TRANSFORMER_FAULT,
)


def test_projection_preserves_identity():
    candidate = project_knowledge_candidate(
        INTERNAL_TRANSFORMER_FAULT
    )

    assert candidate.knowledge_id == "TR-EKO-0001"
    assert candidate.domains == ("transformer",)


def test_projection_extracts_evidence_names():
    candidate = project_knowledge_candidate(
        INTERNAL_TRANSFORMER_FAULT
    )

    assert "Differential relay event report" in (
        candidate.evidence_terms
    )

    assert "COMTRADE waveform" in (
        candidate.evidence_terms
    )

    assert "DGA report" in (
        candidate.evidence_terms
    )


def test_projection_does_not_copy_definition():
    candidate = project_knowledge_candidate(
        INTERNAL_TRANSFORMER_FAULT
    )

    dumped = candidate.__dict__

    assert "definition" not in dumped
    assert "physical_principles" not in dumped
    assert "references" not in dumped
    assert "relationships" not in dumped


def test_projection_leaves_future_metadata_empty():
    candidate = project_knowledge_candidate(
        INTERNAL_TRANSFORMER_FAULT
    )

    assert candidate.asset_types == ()
    assert candidate.investigation_stages == ()
