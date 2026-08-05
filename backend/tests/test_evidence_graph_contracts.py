from app.brain.evidence_graph_contracts import (
    EvidenceEdge,
    EvidenceGraph,
    EvidenceNode,
    EvidenceRelation,
)


def test_creates_empty_graph():
    graph = EvidenceGraph()

    assert graph.nodes == []
    assert graph.edges == []
    assert graph.shadow_only is True
    assert graph.affects_reasoning is False
    assert graph.affects_decision is False


def test_creates_node():
    node = EvidenceNode(
        node_id="n1",
        evidence_id="physics:differential_current",
        evidence_type="differential_current",
        category="physics",
    )

    assert node.node_id == "n1"
    assert node.evidence_type == "differential_current"
    assert node.category == "physics"


def test_creates_edge():
    edge = EvidenceEdge(
        source_node="n1",
        target_node="n2",
        relation=EvidenceRelation.SUPPORTS,
    )

    assert edge.relation == EvidenceRelation.SUPPORTS


def test_graph_contains_nodes_and_edges():
    node1 = EvidenceNode(
        node_id="n1",
        evidence_id="a",
        evidence_type="physics",
        category="physics",
    )

    node2 = EvidenceNode(
        node_id="n2",
        evidence_id="b",
        evidence_type="relay",
        category="protection",
    )

    edge = EvidenceEdge(
        source_node="n1",
        target_node="n2",
        relation=EvidenceRelation.DERIVED_FROM,
    )

    graph = EvidenceGraph(
        nodes=[node1, node2],
        edges=[edge],
    )

    assert len(graph.nodes) == 2
    assert len(graph.edges) == 1
