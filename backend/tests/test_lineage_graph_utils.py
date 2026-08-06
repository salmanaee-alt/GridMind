from app.lineage.contracts import (
    LineageEdge,
    LineageGraph,
    LineageNode,
    LineageNodeType,
    LineageRelation,
)
from app.lineage.graph_utils import (
    build_adjacency,
    find_cycles,
)


def _node(node_id: str) -> LineageNode:
    return LineageNode(
        node_id=node_id,
        node_type=LineageNodeType.EVIDENCE,
        display_name=node_id,
    )


def test_builds_adjacency_for_empty_graph():
    graph = LineageGraph()

    adjacency = build_adjacency(graph)

    assert adjacency == {}


def test_builds_adjacency_with_isolated_nodes():
    graph = LineageGraph(
        nodes=(
            _node("evidence:1"),
            _node("hypothesis:1"),
        ),
    )

    adjacency = build_adjacency(graph)

    assert adjacency == {
        "evidence:1": set(),
        "hypothesis:1": set(),
    }


def test_builds_adjacency_from_edges():
    graph = LineageGraph(
        nodes=(
            _node("hypothesis:1"),
            _node("evidence:1"),
        ),
        edges=(
            LineageEdge(
                source_node="hypothesis:1",
                target_node="evidence:1",
                relation=LineageRelation.SUPPORTS,
            ),
        ),
    )

    adjacency = build_adjacency(graph)

    assert adjacency == {
        "hypothesis:1": {"evidence:1"},
        "evidence:1": set(),
    }


def test_find_cycles_placeholder_returns_empty():
    graph = LineageGraph(
        nodes=(
            _node("evidence:1"),
        ),
    )

    assert find_cycles(graph) == ()


def test_detects_simple_cycle():
    graph = LineageGraph(
        nodes=(
            _node("evidence:1"),
            _node("hypothesis:1"),
        ),
        edges=(
            LineageEdge(
                source_node="evidence:1",
                target_node="hypothesis:1",
                relation=LineageRelation.SUPPORTS,
            ),
            LineageEdge(
                source_node="hypothesis:1",
                target_node="evidence:1",
                relation=LineageRelation.DEPENDS_ON,
            ),
        ),
    )

    assert find_cycles(graph) == (
        (
            "evidence:1",
            "hypothesis:1",
            "evidence:1",
        ),
    )


def test_acyclic_graph_has_no_cycles():
    graph = LineageGraph(
        nodes=(
            _node("decision:1"),
            _node("hypothesis:1"),
            _node("evidence:1"),
        ),
        edges=(
            LineageEdge(
                source_node="decision:1",
                target_node="hypothesis:1",
                relation=LineageRelation.DEPENDS_ON,
            ),
            LineageEdge(
                source_node="hypothesis:1",
                target_node="evidence:1",
                relation=LineageRelation.SUPPORTS,
            ),
        ),
    )

    assert find_cycles(graph) == ()    