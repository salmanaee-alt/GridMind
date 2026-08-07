from app.graph.algorithms.reachability import (
    find_reachable_nodes,
)
from app.graph.contracts import (
    EngineeringGraph,
    GraphEdge,
    GraphNode,
)


def _node(node_id: str):
    return GraphNode(
        node_id=node_id,
        node_type="test",
    )


def test_empty_graph():
    graph = EngineeringGraph(
        graph_id="g",
    )

    assert find_reachable_nodes(
        graph,
        start_node_id="a",
    ) == ()


def test_linear_graph():
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

    assert find_reachable_nodes(
        graph,
        start_node_id="a",
    ) == (
        "a",
        "b",
        "c",
    )


def test_disconnected_graph():
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
        ),
    )

    assert find_reachable_nodes(
        graph,
        start_node_id="a",
    ) == (
        "a",
        "b",
    )


def test_unknown_start():
    graph = EngineeringGraph(
        graph_id="g",
        nodes=(
            _node("a"),
        ),
    )

    assert find_reachable_nodes(
        graph,
        start_node_id="x",
    ) == ()