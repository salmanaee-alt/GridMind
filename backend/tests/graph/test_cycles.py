from app.graph.algorithms.cycles import (
    find_cycles,
)
from app.graph.contracts import (
    EngineeringGraph,
    GraphEdge,
    GraphNode,
)


def _node(node_id: str) -> GraphNode:
    return GraphNode(
        node_id=node_id,
        node_type="test",
    )


def test_empty_graph_has_no_cycles():
    graph = EngineeringGraph(
        graph_id="g",
    )

    assert find_cycles(graph) == ()


def test_acyclic_graph_has_no_cycles():
    graph = EngineeringGraph(
        graph_id="g",
        nodes=(
            _node("a"),
            _node("b"),
            _node("c"),
        ),
        edges=(
            GraphEdge(
                source_node_id="a",
                target_node_id="b",
                relation="edge",
            ),
            GraphEdge(
                source_node_id="b",
                target_node_id="c",
                relation="edge",
            ),
        ),
    )

    assert find_cycles(graph) == ()


def test_detects_simple_cycle():
    graph = EngineeringGraph(
        graph_id="g",
        nodes=(
            _node("a"),
            _node("b"),
        ),
        edges=(
            GraphEdge(
                source_node_id="a",
                target_node_id="b",
                relation="edge",
            ),
            GraphEdge(
                source_node_id="b",
                target_node_id="a",
                relation="edge",
            ),
        ),
    )

    assert find_cycles(graph) == (
        (
            "a",
            "b",
            "a",
        ),
    )


def test_detects_self_cycle():
    graph = EngineeringGraph(
        graph_id="g",
        nodes=(
            _node("a"),
        ),
        edges=(
            GraphEdge(
                source_node_id="a",
                target_node_id="a",
                relation="edge",
            ),
        ),
    )

    assert find_cycles(graph) == (
        (
            "a",
            "a",
        ),
    )