from __future__ import annotations

from collections.abc import Iterable

from app.brain.evidence_contracts import (
    EngineeringEvidence,
)
from app.brain.evidence_graph_contracts import (
    EvidenceEdge,
    EvidenceGraph,
    EvidenceNode,
    EvidenceRelation,
)


_RELATION_MAP = {
    "derived_from": EvidenceRelation.DERIVED_FROM,
    "supports": EvidenceRelation.SUPPORTS,
    "contradicts": EvidenceRelation.CONTRADICTS,
    "validates": EvidenceRelation.VALIDATES,
    "invalidates": EvidenceRelation.INVALIDATES,
    "depends_on": EvidenceRelation.DEPENDS_ON,
}


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

    node_id_by_evidence_id = {
        node.evidence_id: node.node_id
        for node in nodes
    }

    edges: list[EvidenceEdge] = []

    for item in evidence_list:
        source_node = node_id_by_evidence_id[
            item.evidence_id
        ]

        for relationship in item.relationships:
            target_node = node_id_by_evidence_id.get(
                relationship.target_evidence_id
            )

            if target_node is None:
                continue

            edges.append(
                EvidenceEdge(
                    source_node=source_node,
                    target_node=target_node,
                    relation=_RELATION_MAP[
                        relationship.relation.value
                    ],
                )
            )

    return EvidenceGraph(
        nodes=nodes,
        edges=edges,
    )