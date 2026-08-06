from app.lineage.contracts import (
    LineageEdge,
    LineageGraph,
    LineageNode,
    LineageNodeType,
    LineageRelation,
)
from app.lineage.validator import (
    validate_lineage_graph,
)


def _node(node_id: str):
    return LineageNode(
        node_id=node_id,
        node_type=LineageNodeType.EVIDENCE,
        display_name=node_id,
    )


def test_empty_graph_is_valid():
    result = validate_lineage_graph(
        LineageGraph()
    )

    assert result.valid is True


def test_single_node_is_valid():
    graph = LineageGraph(
        nodes=(
            _node("evidence:1"),
        ),
    )

    result = validate_lineage_graph(graph)

    assert result.valid is True


def test_missing_target_is_invalid():
    graph = LineageGraph(
        nodes=(
            _node("evidence:1"),
        ),
        edges=(
            LineageEdge(
                source_node="evidence:1",
                target_node="evidence:2",
                relation=(
                    LineageRelation.SUPPORTS
                ),
            ),
        ),
    )

    result = validate_lineage_graph(graph)

    assert result.valid is False

    assert result.missing_target_nodes == (
        "evidence:2",
    )


def test_missing_source_is_invalid():
    graph = LineageGraph(
        nodes=(
            _node("evidence:1"),
        ),
        edges=(
            LineageEdge(
                source_node="evidence:2",
                target_node="evidence:1",
                relation=(
                    LineageRelation.SUPPORTS
                ),
            ),
        ),
    )

    result = validate_lineage_graph(graph)

    assert result.valid is False

    assert result.missing_source_nodes == (
        "evidence:2",
    )


def test_valid_graph():
    graph = LineageGraph(
        nodes=(
            _node("evidence:1"),
            _node("hypothesis:1"),
        ),
        edges=(
            LineageEdge(
                source_node="hypothesis:1",
                target_node="evidence:1",
                relation=(
                    LineageRelation.SUPPORTS
                ),
            ),
        ),
    )

    result = validate_lineage_graph(graph)

    assert result.valid is True


def test_reports_duplicate_node_ids():
    duplicate = _node("evidence:1")

    graph = LineageGraph(
        nodes=(
            duplicate,
            duplicate,
        ),
    )

    result = validate_lineage_graph(graph)

    assert result.valid is False

    assert result.duplicate_node_ids == (
        "evidence:1",
    )


def test_cycle_makes_graph_invalid():
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

    result = validate_lineage_graph(graph)

    assert result.valid is False
    assert result.cycles == (
        (
            "evidence:1",
            "hypothesis:1",
            "evidence:1",
        ),
    )