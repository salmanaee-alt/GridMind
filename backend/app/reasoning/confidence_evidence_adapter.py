from __future__ import annotations

from app.brain.evidence_graph_contracts import (
    EvidenceGraph,
)
from app.graph.contracts import (
    EngineeringGraph,
    GraphEdge,
    GraphNode,
)
from app.reasoning.confidence_contracts import (
    ConfidencePropagationRequest,
)


def build_confidence_request_from_evidence_graph(
    *,
    graph: EvidenceGraph,
    confidence_scores: dict[
        str,
        float,
    ],
) -> ConfidencePropagationRequest:
    engineering_graph = EngineeringGraph(
        graph_id="confidence-evidence",
        nodes=tuple(
            GraphNode(
                node_id=node.node_id,
                node_type="evidence",
                metadata={
                    "evidence_id":
                        node.evidence_id,
                    "evidence_type":
                        node.evidence_type,
                    "category":
                        node.category,
                },
            )
            for node in graph.nodes
        ),
        edges=tuple(
            GraphEdge(
                source_node_id=(
                    edge.source_node
                ),
                target_node_id=(
                    edge.target_node
                ),
                relation=(
                    edge.relation.value
                ),
            )
            for edge in graph.edges
        ),
        metadata={
            "source_graph":
                "evidence_graph",
            "shadow_only":
                graph.shadow_only,
            "affects_reasoning":
                graph.affects_reasoning,
            "affects_decision":
                graph.affects_decision,
        },
    )

    return ConfidencePropagationRequest(
        graph=engineering_graph,
        confidence_scores=(
            confidence_scores
        ),
    )