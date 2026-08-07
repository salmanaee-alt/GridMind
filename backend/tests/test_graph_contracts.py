import pytest
from pydantic import ValidationError

from app.graph.contracts import (
    EngineeringGraph,
    GraphDirection,
    GraphEdge,
    GraphNode,
)


def test_creates_graph_node():
    node = GraphNode(
        node_id="evidence:1",
        node_type="evidence",
    )

    assert node.node_id == "evidence:1"
    assert node.node_type == "evidence"
    assert node.metadata == {}


def test_creates_graph_edge():
    edge = GraphEdge(
        source_node_id="hypothesis:1",
        target_node_id="evidence:1",
        relation="supports",
    )

    assert edge.source_node_id == "hypothesis:1"
    assert edge.target_node_id == "evidence:1"
    assert edge.relation == "supports"
    assert edge.metadata == {}


def test_creates_directed_graph_by_default():
    graph = EngineeringGraph(
        graph_id="engineering-lineage",
    )

    assert graph.graph_id == "engineering-lineage"
    assert graph.direction == GraphDirection.DIRECTED
    assert graph.nodes == ()
    assert graph.edges == ()


def test_creates_graph_with_nodes_and_edges():
    node_a = GraphNode(
        node_id="hypothesis:1",
        node_type="hypothesis",
    )

    node_b = GraphNode(
        node_id="evidence:1",
        node_type="evidence",
    )

    edge = GraphEdge(
        source_node_id=node_a.node_id,
        target_node_id=node_b.node_id,
        relation="supports",
    )

    graph = EngineeringGraph(
        graph_id="test-graph",
        nodes=(node_a, node_b),
        edges=(edge,),
    )

    assert len(graph.nodes) == 2
    assert len(graph.edges) == 1


def test_graph_models_are_immutable():
    node = GraphNode(
        node_id="evidence:1",
        node_type="evidence",
    )

    with pytest.raises(ValidationError):
        node.node_type = "changed"


def test_graph_models_reject_extra_fields():
    with pytest.raises(ValidationError):
        GraphNode(
            node_id="evidence:1",
            node_type="evidence",
            unexpected=True,
        )


def test_node_rejects_blank_identifier():
    with pytest.raises(ValidationError):
        GraphNode(
            node_id="",
            node_type="evidence",
        )


def test_edge_rejects_blank_relation():
    with pytest.raises(ValidationError):
        GraphEdge(
            source_node_id="a",
            target_node_id="b",
            relation="",
        )