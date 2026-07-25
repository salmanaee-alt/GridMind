from __future__ import annotations

from app.capabilities.traceable_context.contracts import (
    ProvenanceGapType,    
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
	    provenance_gap=(
    		ProvenanceGapType.NONE
   		if item.supporting_knowledge_ids
 		else ProvenanceGapType.NO_SUPPORTING_KNOWLEDGE
	    ),
        )
        for item in request.evidence_items
    )

    interpreted_evidence_count = len(
        evidence_items
    )

    traced_evidence = tuple(
        item
        for item in evidence_items
        if item.supporting_knowledge_ids
    )

    traced_evidence_count = len(
        traced_evidence
    )

    untraced_evidence = tuple(
        item.evidence
        for item in evidence_items
        if not item.supporting_knowledge_ids
    )

    untraced_evidence_count = len(
        untraced_evidence
    )

    if interpreted_evidence_count == 0:
        traceability_ratio = 0.0
    else:
        traceability_ratio = round(
            traced_evidence_count
            / interpreted_evidence_count,
            4,
        )

    traceability_complete = (
        interpreted_evidence_count > 0
        and traced_evidence_count
        == interpreted_evidence_count
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
        interpreted_evidence_count=(
            interpreted_evidence_count
        ),
        traced_evidence_count=(
            traced_evidence_count
        ),
        untraced_evidence_count=(
            untraced_evidence_count
        ),
        traceability_ratio=(
            traceability_ratio
        ),
        untraced_evidence=(
            untraced_evidence
        ),
        affects_decision=False,
    )
