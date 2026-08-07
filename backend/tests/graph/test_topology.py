from app.graph.algorithms.topology import (
    topological_sort,
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


def test_empty_graph_returns_empty_order():
    graph = EngineeringGraph(
        graph_id="g",
    )

    assert topological_sort(graph) == ()


def test_single_node_returns_single_node():
    graph = EngineeringGraph(
        graph_id="g",
        nodes=(
            _node("a"),
        ),
    )

    assert topological_sort(graph) == (
        "a",
    )


def test_linear_graph_returns_topological_order():
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

    assert topological_sort(graph) == (
        "a",
        "b",
        "c",
    )


def test_branching_graph_returns_stable_order():
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
                source_node_id="a",
                target_node_id="c",
                relation="edge",
            ),
        ),
    )

    assert topological_sort(graph) == (
        "a",
        "b",
        "c",
    )


def test_cycle_returns_empty_order():
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

    assert topological_sort(graph) == ()