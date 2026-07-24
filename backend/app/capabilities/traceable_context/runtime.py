from __future__ import annotations

from app.capabilities.traceable_context.contracts import (
    TraceableEngineeringContextRequest,
    TraceableEngineeringContextResult,
    TraceableEvidenceItem,
)


def execute_traceable_context(
    *,
    request: TraceableEngineeringContextRequest,
) -> TraceableEngineeringContextResult:
    """
    Assemble traceable engineering context conservatively.

    This runtime does not infer new relationships between
    evidence and knowledge. It preserves only explicitly
    provided traceability.
    """

    if not isinstance(
        request,
        TraceableEngineeringContextRequest,
    ):
        raise TypeError(
            "execute_traceable_context requires a "
            "TraceableEngineeringContextRequest."
        )

    evidence_items = tuple(
        TraceableEvidenceItem(
            evidence=item.evidence,
            interpretation=item.interpretation,
            engineering_significance=(
                item.engineering_significance
            ),
            supporting_knowledge_ids=(
                item.supporting_knowledge_ids
            ),
        )
        for item in request.evidence_items
    )

    traceability_complete = (
        bool(evidence_items)
        and all(
            item.supporting_knowledge_ids
            for item in evidence_items
        )
        and not request.unresolved_evidence
    )

    return TraceableEngineeringContextResult(
        knowledge_ids=(
            request.selected_knowledge_ids
        ),
        evidence_items=evidence_items,
        unresolved_evidence=(
            request.unresolved_evidence
        ),
        traceability_complete=(
            traceability_complete
        ),
        affects_decision=False,
    )
