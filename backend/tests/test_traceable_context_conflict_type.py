from app.capabilities.traceable_context.contracts import (
    EvidenceConflictType,
    TraceableEngineeringContextRequest,
)
from app.capabilities.traceable_context.runtime import (
    execute_traceable_context,
)


def _request():
    return TraceableEngineeringContextRequest(
        domain="power_systems",
        asset_type="transformer",
        investigation_stage="differential_trip_analysis",
        selected_knowledge_ids=("K-001",),
        evidence_items=(
            {
                "evidence": "Relay trip received",
                "interpretation": "Protection operated",
                "engineering_significance": "Trip indication",
                "supporting_knowledge_ids": ("K-001",),
            },
        ),
        unresolved_evidence=(),
    )


def test_conflict_type_defaults_to_none():
    result = execute_traceable_context(
        request=_request()
    )

    assert (
        result.evidence_items[0].conflict_type
        == EvidenceConflictType.NONE
    )


def test_conflict_type_does_not_change_traceability():
    result = execute_traceable_context(
        request=_request()
    )

    assert result.traceability_complete is True
    assert result.interpreted_evidence_count == 1
    assert result.traced_evidence_count == 1
    assert result.untraced_evidence_count == 0
    assert result.traceability_ratio == 1.0


def test_conflict_type_does_not_change_provenance():
    result = execute_traceable_context(
        request=_request()
    )

    assert (
        result.evidence_items[0].provenance_gap.value
        == "none"
    )


def test_missing_support_is_classified():
    request = TraceableEngineeringContextRequest(
        domain="power_systems",
        asset_type="transformer",
        investigation_stage="differential_trip_analysis",
        selected_knowledge_ids=("K-001",),
        evidence_items=(
            {
                "evidence": "Unverified alarm observed",
                "interpretation": "Possible abnormal condition",
                "engineering_significance": "Requires verification",
                "supporting_knowledge_ids": (),
            },
        ),
        unresolved_evidence=(),
    )

    result = execute_traceable_context(
        request=request
    )

    assert (
        result.evidence_items[0].conflict_type
        == EvidenceConflictType.MISSING_SUPPORT
    )


def test_missing_support_requires_verification():
    request = TraceableEngineeringContextRequest(
        domain="power_systems",
        asset_type="transformer",
        investigation_stage="differential_trip_analysis",
        selected_knowledge_ids=("K-001",),
        evidence_items=(
            {
                "evidence": "Unverified alarm observed",
                "interpretation": "Possible abnormal condition",
                "engineering_significance": "Requires verification",
                "supporting_knowledge_ids": (),
            },
        ),
        unresolved_evidence=(),
    )

    result = execute_traceable_context(
        request=request
    )

    assert (
        result.evidence_items[0].conflict_status.value
        == "verification_required"
    )
    