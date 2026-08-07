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
from app.graph.builder import (
    GraphBuilder,
)
from app.graph.contracts import (
    GraphEdge,
    GraphNode,
)


_RELATION_MAP = {
    "derived_from": EvidenceRelation.DERIVED_FROM,
    "supports": EvidenceRelation.SUPPORTS,
    "contradicts": EvidenceRelation.CONTRADICTS,
    "validates": EvidenceRelation.VALIDATES,
    "invalidates": EvidenceRelation.INVALIDATES,
    "depends_on": EvidenceRelation.DEPENDS_ON,
}


def _to_graph_node(
    node: EvidenceNode,
) -> GraphNode:
    return GraphNode(
        node_id=node.node_id,
        node_type="evidence",
        metadata={
            "evidence_id": node.evidence_id,
            "evidence_type": node.evidence_type,
            "category": node.category,
        },
    )


def _to_graph_edge(
    edge: EvidenceEdge,
) -> GraphEdge:
    return GraphEdge(
        source_node_id=edge.source_node,
        target_node_id=edge.target_node,
        relation=edge.relation.value,
    )


def build_evidence_graph(
    evidence_items: Iterable[EngineeringEvidence],
) -> EvidenceGraph:
    evidence_list = list(evidence_items)

    evidence_nodes = [
        EvidenceNode(
            node_id=(
                f"evidence-node:{item.evidence_id}"
            ),
            evidence_id=item.evidence_id,
            evidence_type=item.evidence_type,
            category=item.category.value,
        )
        for item in evidence_list
    ]

    node_id_by_evidence_id = {
        node.evidence_id: node.node_id
        for node in evidence_nodes
    }

    evidence_edges: list[EvidenceEdge] = []

    for item in evidence_list:
        source_node = node_id_by_evidence_id[
            item.evidence_id
        ]

        for relationship in item.relationships:
            target_node = (
                node_id_by_evidence_id.get(
                    relationship.target_evidence_id
                )
            )

            if target_node is None:
                continue

            evidence_edges.append(
                EvidenceEdge(
                    source_node=source_node,
                    target_node=target_node,
                    relation=_RELATION_MAP[
                        relationship.relation.value
                    ],
                )
            )

    engineering_graph = (
        GraphBuilder()
        .set_graph_id("engineering-evidence")
        .set_metadata(
            graph_type="evidence_graph",
            evidence_count=len(evidence_list),
        )
        .add_nodes(
            tuple(
                _to_graph_node(node)
                for node in evidence_nodes
            )
        )
        .add_edges(
            tuple(
                _to_graph_edge(edge)
                for edge in evidence_edges
            )
        )
        .build()
    )

    return EvidenceGraph(
        nodes=[
            EvidenceNode(
                node_id=node.node_id,
                evidence_id=str(
                    node.metadata["evidence_id"]
                ),
                evidence_type=str(
                    node.metadata["evidence_type"]
                ),
                category=str(
                    node.metadata["category"]
                ),
            )
            for node in engineering_graph.nodes
        ],
        edges=[
            EvidenceEdge(
                source_node=edge.source_node_id,
                target_node=edge.target_node_id,
                relation=EvidenceRelation(
                    edge.relation
                ),
            )
            for edge in engineering_graph.edges
        ],
    )