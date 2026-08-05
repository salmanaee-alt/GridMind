from __future__ import annotations

from pydantic import BaseModel, Field

from app.brain.evidence_graph_contracts import (
    EvidenceGraph,
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


def _find_duplicates(values: list[str]) -> list[str]:
    seen: set[str] = set()
    duplicates: set[str] = set()

    for value in values:
        if value in seen:
            duplicates.add(value)
        else:
            seen.add(value)

    return sorted(duplicates)


def validate_evidence_graph(
    graph: EvidenceGraph,
) -> EvidenceGraphValidationResult:
    node_ids = [
        node.node_id
        for node in graph.nodes
    ]

    evidence_ids = [
        node.evidence_id
        for node in graph.nodes
    ]

    known_node_ids = set(node_ids)

    missing_source_nodes = sorted({
        edge.source_node
        for edge in graph.edges
        if edge.source_node not in known_node_ids
    })

    missing_target_nodes = sorted({
        edge.target_node
        for edge in graph.edges
        if edge.target_node not in known_node_ids
    })

    duplicate_node_ids = _find_duplicates(node_ids)
    duplicate_evidence_ids = _find_duplicates(
        evidence_ids
    )

    valid = not any([
        duplicate_node_ids,
        duplicate_evidence_ids,
        missing_source_nodes,
        missing_target_nodes,
    ])

    return EvidenceGraphValidationResult(
        valid=valid,
        duplicate_node_ids=duplicate_node_ids,
        duplicate_evidence_ids=duplicate_evidence_ids,
        missing_source_nodes=missing_source_nodes,
        missing_target_nodes=missing_target_nodes,
    )
