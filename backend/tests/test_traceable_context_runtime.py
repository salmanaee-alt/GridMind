from app.capabilities.traceable_context.contracts import (
    TraceableEngineeringContextRequest,
    TraceableEvidenceItem,
)
from app.capabilities.traceable_context.runtime import (
    execute_traceable_context,
)


def test_runtime_preserves_explicit_traceability() -> None:
    result = execute_traceable_context(
        request=TraceableEngineeringContextRequest(
            domain="transformer",
            asset_type="power_transformer",
            investigation_stage="initial",
            selected_knowledge_ids=(
                "EKO-0001",
            ),
            evidence_items=(
                TraceableEvidenceItem(
                    evidence="DGA report",
                    interpretation="DGA interpretation",
                    engineering_significance=(
                        "Transformer condition evidence."
                    ),
                    supporting_knowledge_ids=(
                        "EKO-0001",
                    ),
                ),
            ),
        ),
    )

    assert result.knowledge_ids == (
        "EKO-0001",
    )

    assert result.evidence_items[
        0
    ].supporting_knowledge_ids == (
        "EKO-0001",
    )

    assert result.traceability_complete is True
    assert result.affects_decision is False


def test_runtime_does_not_invent_knowledge_links() -> None:
    result = execute_traceable_context(
        request=TraceableEngineeringContextRequest(
            domain="transformer",
            asset_type="power_transformer",
            investigation_stage="initial",
            selected_knowledge_ids=(
                "EKO-0001",
            ),
            evidence_items=(
                TraceableEvidenceItem(
                    evidence="DGA report",
                    interpretation="DGA interpretation",
                    engineering_significance=(
                        "Transformer condition evidence."
                    ),
                ),
            ),
        ),
    )

    assert result.evidence_items[
        0
    ].supporting_knowledge_ids == ()

    assert result.traceability_complete is False


def test_runtime_marks_unresolved_evidence_incomplete() -> None:
    result = execute_traceable_context(
        request=TraceableEngineeringContextRequest(
            domain="transformer",
            asset_type="power_transformer",
            investigation_stage="initial",
            selected_knowledge_ids=(
                "EKO-0001",
            ),
            evidence_items=(
                TraceableEvidenceItem(
                    evidence="DGA report",
                    interpretation="DGA interpretation",
                    engineering_significance="Significance",
                    supporting_knowledge_ids=(
                        "EKO-0001",
                    ),
                ),
            ),
            unresolved_evidence=(
                "Unknown diagnostic flag",
            ),
        ),
    )

    assert result.traceability_complete is False
    assert result.unresolved_evidence == (
        "Unknown diagnostic flag",
    )


def test_runtime_empty_context_is_not_complete() -> None:
    result = execute_traceable_context(
        request=TraceableEngineeringContextRequest(
            domain="transformer",
            asset_type="power_transformer",
            investigation_stage="initial",
        ),
    )

    assert result.knowledge_ids == ()
    assert result.evidence_items == ()
    assert result.unresolved_evidence == ()
    assert result.traceability_complete is False
    assert result.affects_decision is False
    