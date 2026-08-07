from app.graph.contracts import (
    EngineeringGraph,
    GraphEdge,
    GraphNode,
)
from app.graph.algorithms.traversal import (
    breadth_first_traversal,
    build_adjacency,
    depth_first_traversal,
)


def _node(node_id: str):
    return GraphNode(
        node_id=node_id,
        node_type="test",
    )


def test_build_adjacency():
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
        ),
    )

    assert build_adjacency(graph) == {
        "a": {"b"},
        "b": set(),
    }


def test_depth_first_traversal():
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

    assert depth_first_traversal(
        graph,
        start_node_id="a",
    ) == (
        "a",
        "b",
        "c",
    )


def test_breadth_first_traversal():
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

    assert breadth_first_traversal(
        graph,
        start_node_id="a",
    ) == (
        "a",
        "b",
        "c",
    )


def test_unknown_start_node_returns_empty():
    graph = EngineeringGraph(
        graph_id="g",
    )

    assert depth_first_traversal(
        graph,
        start_node_id="x",
    ) == ()

    assert breadth_first_traversal(
        graph,
        start_node_id="x",
    ) == ()