from app.graph.contracts import (
    EngineeringGraph,
    GraphEdge,
    GraphNode,
)
from app.graph.validation import (
    validate_graph,
)


def _node(node_id: str) -> GraphNode:
    return GraphNode(
        node_id=node_id,
        node_type="test",
    )


def _edge(
    source_node_id: str,
    target_node_id: str,
    relation: str = "edge",
) -> GraphEdge:
    return GraphEdge(
        source_node_id=source_node_id,
        target_node_id=target_node_id,
        relation=relation,
    )


def test_empty_graph_is_valid():
    graph = EngineeringGraph(
        graph_id="empty",
    )

    result = validate_graph(graph)

    assert result.valid is True
    assert result.duplicate_node_ids == ()
    assert result.duplicate_edges == ()
    assert result.missing_source_nodes == ()
    assert result.missing_target_nodes == ()
    assert result.orphan_nodes == ()
    assert result.cycles == ()
    assert result.affects_reasoning is False
    assert result.affects_decision is False


def test_valid_connected_graph():
    graph = EngineeringGraph(
        graph_id="valid",
        nodes=(
            _node("a"),
            _node("b"),
        ),
        edges=(
            _edge("a", "b"),
        ),
    )

    result = validate_graph(graph)

    assert result.valid is True
    assert result.duplicate_node_ids == ()
    assert result.duplicate_edges == ()
    assert result.missing_source_nodes == ()
    assert result.missing_target_nodes == ()
    assert result.orphan_nodes == ()
    assert result.cycles == ()


def test_detects_duplicate_node_ids():
    graph = EngineeringGraph(
        graph_id="duplicate-nodes",
        nodes=(
            _node("a"),
            _node("a"),
        ),
    )

    result = validate_graph(graph)

    assert result.valid is False
    assert result.duplicate_node_ids == ("a",)


def test_detects_duplicate_edges():
    duplicate_edge = _edge(
        "a",
        "b",
        relation="supports",
    )

    graph = EngineeringGraph(
        graph_id="duplicate-edges",
        nodes=(
            _node("a"),
            _node("b"),
        ),
        edges=(
            duplicate_edge,
            duplicate_edge,
        ),
    )

    result = validate_graph(graph)

    assert result.valid is False
    assert result.duplicate_edges == (
        "a|b|supports",
    )


def test_detects_missing_source_node():
    graph = EngineeringGraph(
        graph_id="missing-source",
        nodes=(
            _node("b"),
        ),
        edges=(
            _edge("missing", "b"),
        ),
    )

    result = validate_graph(graph)

    assert result.valid is False
    assert result.missing_source_nodes == (
        "missing",
    )
    assert result.missing_target_nodes == ()


def test_detects_missing_target_node():
    graph = EngineeringGraph(
        graph_id="missing-target",
        nodes=(
            _node("a"),
        ),
        edges=(
            _edge("a", "missing"),
        ),
    )

    result = validate_graph(graph)

    assert result.valid is False
    assert result.missing_source_nodes == ()
    assert result.missing_target_nodes == (
        "missing",
    )


def test_reports_orphan_nodes_without_invalidating_graph():
    graph = EngineeringGraph(
        graph_id="orphan",
        nodes=(
            _node("a"),
            _node("b"),
            _node("orphan"),
        ),
        edges=(
            _edge("a", "b"),
        ),
    )

    result = validate_graph(graph)

    assert result.valid is True
    assert result.orphan_nodes == (
        "orphan",
    )


def test_detects_cycle():
    graph = EngineeringGraph(
        graph_id="cycle",
        nodes=(
            _node("a"),
            _node("b"),
        ),
        edges=(
            _edge("a", "b"),
            _edge("b", "a"),
        ),
    )

    result = validate_graph(graph)

    assert result.valid is False
    assert result.cycles == (
        (
            "a",
            "b",
            "a",
        ),
    )


def test_reports_all_structural_failures_together():
    duplicate_edge = _edge(
        "a",
        "missing",
        relation="supports",
    )

    graph = EngineeringGraph(
        graph_id="multiple-errors",
        nodes=(
            _node("a"),
            _node("a"),
            _node("orphan"),
        ),
        edges=(
            duplicate_edge,
            duplicate_edge,
            _edge("unknown", "a"),
        ),
    )

    result = validate_graph(graph)

    assert result.valid is False
    assert result.duplicate_node_ids == (
        "a",
    )
    assert result.duplicate_edges == (
        "a|missing|supports",
    )
    assert result.missing_source_nodes == (
        "unknown",
    )
    assert result.missing_target_nodes == (
        "missing",
    )
    assert result.orphan_nodes == (
        "orphan",
    )