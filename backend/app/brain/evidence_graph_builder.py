from __future__ import annotations

from collections.abc import Iterable

from app.brain.evidence_contracts import EngineeringEvidence
from app.brain.evidence_graph_contracts import (
    EvidenceGraph,
    EvidenceNode,
)


def build_evidence_graph(
    evidence_items: Iterable[EngineeringEvidence],
) -> EvidenceGraph:
    evidence_list = list(evidence_items)

    nodes = [
        EvidenceNode(
            node_id=f"evidence-node:{item.evidence_id}",
            evidence_id=item.evidence_id,
            evidence_type=item.evidence_type,
            category=item.category.value,
        )
        for item in evidence_list
    ]

    return EvidenceGraph(
        nodes=nodes,
        edges=[],
    )
