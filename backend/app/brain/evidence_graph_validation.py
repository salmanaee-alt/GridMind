from __future__ import annotations

from pydantic import BaseModel, Field

from app.brain.evidence_graph_contracts import (
    EvidenceGraph,
)
from app.graph.contracts import (
    EngineeringGraph,
    GraphEdge,
    GraphNode,
)
from app.graph.validation import (
    validate_graph,
)


class EvidenceGraphValidationResult(BaseModel):
    valid: bool

    duplicate_node_ids: list[str] = Field(
        default_factory=list
    )
    duplicate_evidence_ids: list[str] = Field(
        default_factory=list
    )
    missing_source_nodes: list[str] = Field(
        default_factory=list
    )
    missing_target_nodes: list[str] = Field(
        default_factory=list
    )

    affects_reasoning: bool = False
    affects_decision: bool = False


def _find_duplicates(
    values: list[str],
) -> list[str]:
    seen: set[str] = set()
    duplicates: set[str] = set()

    for value in values:
        if value in seen:
            duplicates.add(value)
        else:
            seen.add(value)

    return sorted(duplicates)


def _to_engineering_graph(
    graph: EvidenceGraph,
) -> EngineeringGraph:
    return EngineeringGraph(
        graph_id="evidence-validation",
        nodes=tuple(
            GraphNode(
                node_id=node.node_id,
                node_type="evidence",
                metadata={
                    "evidence_id": node.evidence_id,
                    "evidence_type": node.evidence_type,
                    "category": node.category,
                },
            )
            for node in graph.nodes
        ),
        edges=tuple(
            GraphEdge(
                source_node_id=edge.source_node,
                target_node_id=edge.target_node,
                relation=edge.relation.value,
            )
            for edge in graph.edges
        ),
    )


def validate_evidence_graph(
    graph: EvidenceGraph,
) -> EvidenceGraphValidationResult:
    engineering_graph = _to_engineering_graph(
        graph
    )

    graph_validation = validate_graph(
        engineering_graph
    )

    evidence_ids = [
        node.evidence_id
        for node in graph.nodes
    ]

    duplicate_evidence_ids = _find_duplicates(
        evidence_ids
    )

    valid = (
        graph_validation.valid
        and not duplicate_evidence_ids
    )

    return EvidenceGraphValidationResult(
        valid=valid,
        duplicate_node_ids=list(
            graph_validation.duplicate_node_ids
        ),
        duplicate_evidence_ids=(
            duplicate_evidence_ids
        ),
        missing_source_nodes=list(
            graph_validation.missing_source_nodes
        ),
        missing_target_nodes=list(
            graph_validation.missing_target_nodes
        ),
    )