from app.graph.algorithms.connectivity import (
    build_undirected_adjacency,
    find_connected_components,
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


def test_empty_graph_has_no_components():
    graph = EngineeringGraph(
        graph_id="g",
    )

    assert find_connected_components(graph) == ()


def test_single_node_is_one_component():
    graph = EngineeringGraph(
        graph_id="g",
        nodes=(
            _node("a"),
        ),
    )

    assert find_connected_components(graph) == (
        ("a",),
    )


def test_connected_graph_has_one_component():
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

    assert find_connected_components(graph) == (
        ("a", "b", "c"),
    )


def test_disconnected_graph_has_multiple_components():
    graph = EngineeringGraph(
        graph_id="g",
        nodes=(
            _node("a"),
            _node("b"),
            _node("c"),
            _node("d"),
        ),
        edges=(
            GraphEdge(
                source_node_id="a",
                target_node_id="b",
                relation="edge",
            ),
            GraphEdge(
                source_node_id="c",
                target_node_id="d",
                relation="edge",
            ),
        ),
    )

    assert find_connected_components(graph) == (
        ("a", "b"),
        ("c", "d"),
    )


def test_builds_undirected_adjacency():
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

    assert build_undirected_adjacency(
        graph
    ) == {
        "a": {"b"},
        "b": {"a"},
    }