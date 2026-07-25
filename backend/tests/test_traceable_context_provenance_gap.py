from app.capabilities.traceable_context.contracts import (
    ProvenanceGapType,
    TraceableEngineeringContextRequest,
    TraceableEvidenceItem,
)
from app.capabilities.traceable_context.runtime import execute_traceable_context


def test_traced_evidence_has_no_provenance_gap():
    request = TraceableEngineeringContextRequest(
        domain="transformer",
        asset_type="power_transformer",
        investigation_stage="diagnosis",
        selected_knowledge_ids=("K-001",),
        evidence_items=(
            TraceableEvidenceItem(
                evidence="Differential relay operated.",
                interpretation="Internal fault indication.",
                engineering_significance="Supports internal fault hypothesis.",
                supporting_knowledge_ids=("K-001",),
            ),
        ),
    )

    result = execute_traceable_context(request=request)

    assert result.evidence_items[0].provenance_gap == ProvenanceGapType.NONE


def test_untraced_evidence_is_classified_as_no_supporting_knowledge():
    request = TraceableEngineeringContextRequest(
        domain="transformer",
        asset_type="power_transformer",
        investigation_stage="diagnosis",
        selected_knowledge_ids=("K-001",),
        evidence_items=(
            TraceableEvidenceItem(
                evidence="Buchholz alarm observed.",
                interpretation="Possible internal gas generation.",
                engineering_significance="Requires further investigation.",
                supporting_knowledge_ids=(),
            ),
        ),
    )

    result = execute_traceable_context(request=request)

    assert (
        result.evidence_items[0].provenance_gap
        == ProvenanceGapType.NO_SUPPORTING_KNOWLEDGE
    )


def test_provenance_gap_classification_does_not_change_coverage_metrics():
    request = TraceableEngineeringContextRequest(
        domain="transformer",
        asset_type="power_transformer",
        investigation_stage="diagnosis",
        selected_knowledge_ids=("K-001",),
        evidence_items=(
            TraceableEvidenceItem(
                evidence="Evidence A",
                interpretation="Interpretation A",
                engineering_significance="Significance A",
                supporting_knowledge_ids=("K-001",),
            ),
            TraceableEvidenceItem(
                evidence="Evidence B",
                interpretation="Interpretation B",
                engineering_significance="Significance B",
                supporting_knowledge_ids=(),
            ),
        ),
    )

    result = execute_traceable_context(request=request)

    assert result.interpreted_evidence_count == 2
    assert result.traced_evidence_count == 1
    assert result.untraced_evidence_count == 1
    assert result.traceability_ratio == 0.5

