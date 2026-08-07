from app.graph.builder import (
    GraphBuilder,
)
from app.graph.contracts import (
    GraphEdge,
    GraphNode,
)


def _node(node_id: str) -> GraphNode:
    return GraphNode(
        node_id=node_id,
        node_type="test",
    )


def _edge(
    source: str,
    target: str,
    relation: str = "edge",
) -> GraphEdge:
    return GraphEdge(
        source_node_id=source,
        target_node_id=target,
        relation=relation,
    )


def test_build_empty_graph():
    graph = (
        GraphBuilder()
        .set_graph_id("g")
        .build()
    )

    assert graph.graph_id == "g"
    assert graph.nodes == ()
    assert graph.edges == ()
    assert graph.metadata == {}


def test_add_single_node():
    graph = (
        GraphBuilder()
        .set_graph_id("g")
        .add_node(_node("a"))
        .build()
    )

    assert len(graph.nodes) == 1
    assert graph.nodes[0].node_id == "a"


def test_add_multiple_nodes():
    graph = (
        GraphBuilder()
        .set_graph_id("g")
        .add_nodes(
            (
                _node("c"),
                _node("a"),
                _node("b"),
            )
        )
        .build()
    )

    assert tuple(
        node.node_id
        for node in graph.nodes
    ) == (
        "a",
        "b",
        "c",
    )


def test_duplicate_node_is_overwritten():
    graph = (
        GraphBuilder()
        .set_graph_id("g")
        .add_node(_node("a"))
        .add_node(_node("a"))
        .build()
    )

    assert len(graph.nodes) == 1


def test_duplicate_edge_is_overwritten():
    edge = _edge(
        "a",
        "b",
        relation="supports",
    )

    graph = (
        GraphBuilder()
        .set_graph_id("g")
        .add_nodes(
            (
                _node("a"),
                _node("b"),
            )
        )
        .add_edge(edge)
        .add_edge(edge)
        .build()
    )

    assert len(graph.edges) == 1


def test_build_complete_graph():
    graph = (
        GraphBuilder()
        .set_graph_id("engineering")
        .set_metadata(
            source="unit-test",
            version="1",
        )
        .add_nodes(
            (
                _node("a"),
                _node("b"),
            )
        )
        .add_edge(
            _edge(
                "a",
                "b",
                relation="supports",
            )
        )
        .build()
    )

    assert graph.graph_id == "engineering"

    assert tuple(
        node.node_id
        for node in graph.nodes
    ) == (
        "a",
        "b",
    )

    assert len(graph.edges) == 1

    assert graph.metadata == {
        "source": "unit-test",
        "version": "1",
    }