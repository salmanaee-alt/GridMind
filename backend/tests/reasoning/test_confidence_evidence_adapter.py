import pytest

from pydantic import ValidationError

from app.brain.evidence_graph_contracts import (
    EvidenceEdge,
    EvidenceGraph,
    EvidenceNode,
    EvidenceRelation,
)
from app.reasoning.confidence_contracts import (
    ConfidencePropagationRequest,
)
from app.reasoning.confidence_evidence_adapter import (
    build_confidence_request_from_evidence_graph,
)


def build_evidence_graph():
    return EvidenceGraph(
        nodes=[
            EvidenceNode(
                node_id="evidence-node:e1",
                evidence_id="e1",
                evidence_type="relay",
                category="protection",
            ),
            EvidenceNode(
                node_id="evidence-node:e2",
                evidence_id="e2",
                evidence_type="dga",
                category="condition",
            ),
        ],
        edges=[
            EvidenceEdge(
                source_node="evidence-node:e1",
                target_node="evidence-node:e2",
                relation=EvidenceRelation.SUPPORTS,
            ),
        ],
    )


def test_adapter_returns_typed_confidence_request():
    request = (
        build_confidence_request_from_evidence_graph(
            graph=build_evidence_graph(),
            confidence_scores={
                "evidence-node:e1": 0.80,
            },
        )
    )

    assert isinstance(
        request,
        ConfidencePropagationRequest,
    )


def test_adapter_preserves_evidence_nodes():
    request = (
        build_confidence_request_from_evidence_graph(
            graph=build_evidence_graph(),
            confidence_scores={
                "evidence-node:e1": 0.80,
            },
        )
    )

    assert {
        node.node_id
        for node in request.graph.nodes
    } == {
        "evidence-node:e1",
        "evidence-node:e2",
    }


def test_adapter_preserves_evidence_edges():
    request = (
        build_confidence_request_from_evidence_graph(
            graph=build_evidence_graph(),
            confidence_scores={
                "evidence-node:e1": 0.80,
            },
        )
    )

    edge = request.graph.edges[0]

    assert edge.source_node_id == (
        "evidence-node:e1"
    )
    assert edge.target_node_id == (
        "evidence-node:e2"
    )
    assert edge.relation == "supports"


def test_adapter_preserves_node_provenance_metadata():
    request = (
        build_confidence_request_from_evidence_graph(
            graph=build_evidence_graph(),
            confidence_scores={
                "evidence-node:e1": 0.80,
            },
        )
    )

    node = request.graph.nodes[0]

    assert node.metadata["evidence_id"] == "e1"
    assert node.metadata["evidence_type"] == "relay"
    assert node.metadata["category"] == "protection"


def test_adapter_does_not_invent_confidence_scores():
    request = (
        build_confidence_request_from_evidence_graph(
            graph=build_evidence_graph(),
            confidence_scores={},
        )
    )

    assert request.confidence_scores == {}


def test_adapter_rejects_score_for_unknown_evidence_node():
    with pytest.raises(ValidationError):
        build_confidence_request_from_evidence_graph(
            graph=build_evidence_graph(),
            confidence_scores={
                "evidence-node:unknown": 0.80,
            },
        )