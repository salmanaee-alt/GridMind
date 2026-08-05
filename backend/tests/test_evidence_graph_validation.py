from app.brain.evidence_graph_contracts import (
    EvidenceEdge,
    EvidenceGraph,
    EvidenceNode,
    EvidenceRelation,
)
from app.brain.evidence_graph_validation import (
    validate_evidence_graph,
)


def _node(
    node_id: str,
    evidence_id: str,
) -> EvidenceNode:
    return EvidenceNode(
        node_id=node_id,
        evidence_id=evidence_id,
        evidence_type="physics",
        category="physics",
    )


def test_empty_graph_is_valid():
    result = validate_evidence_graph(
        EvidenceGraph()
    )

    assert result.valid is True
    assert result.duplicate_node_ids == []
    assert result.duplicate_evidence_ids == []
    assert result.missing_source_nodes == []
    assert result.missing_target_nodes == []
    assert result.affects_reasoning is False
    assert result.affects_decision is False


def test_valid_graph_passes_validation():
    graph = EvidenceGraph(
        nodes=[
            _node("n1", "e1"),
            _node("n2", "e2"),
        ],
        edges=[
            EvidenceEdge(
                source_node="n1",
                target_node="n2",
                relation=EvidenceRelation.DERIVED_FROM,
            )
        ],
    )

    result = validate_evidence_graph(graph)

    assert result.valid is True


def test_detects_duplicate_node_ids():
    graph = EvidenceGraph(
        nodes=[
            _node("n1", "e1"),
            _node("n1", "e2"),
        ]
    )

    result = validate_evidence_graph(graph)

    assert result.valid is False
    assert result.duplicate_node_ids == ["n1"]


def test_detects_duplicate_evidence_ids():
    graph = EvidenceGraph(
        nodes=[
            _node("n1", "e1"),
            _node("n2", "e1"),
        ]
    )

    result = validate_evidence_graph(graph)

    assert result.valid is False
    assert result.duplicate_evidence_ids == ["e1"]


def test_detects_missing_edge_source_node():
    graph = EvidenceGraph(
        nodes=[
            _node("n1", "e1"),
        ],
        edges=[
            EvidenceEdge(
                source_node="missing",
                target_node="n1",
                relation=EvidenceRelation.SUPPORTS,
            )
        ],
    )

    result = validate_evidence_graph(graph)

    assert result.valid is False
    assert result.missing_source_nodes == [
        "missing"
    ]


def test_detects_missing_edge_target_node():
    graph = EvidenceGraph(
        nodes=[
            _node("n1", "e1"),
        ],
        edges=[
            EvidenceEdge(
                source_node="n1",
                target_node="missing",
                relation=EvidenceRelation.CONTRADICTS,
            )
        ],
    )

    result = validate_evidence_graph(graph)

    assert result.valid is False
    assert result.missing_target_nodes == [
        "missing"
    ]


def test_reports_all_integrity_failures_together():
    graph = EvidenceGraph(
        nodes=[
            _node("n1", "e1"),
            _node("n1", "e1"),
        ],
        edges=[
            EvidenceEdge(
                source_node="missing-source",
                target_node="missing-target",
                relation=EvidenceRelation.VALIDATES,
            )
        ],
    )

    result = validate_evidence_graph(graph)

    assert result.valid is False
    assert result.duplicate_node_ids == ["n1"]
    assert result.duplicate_evidence_ids == ["e1"]
    assert result.missing_source_nodes == [
        "missing-source"
    ]
    assert result.missing_target_nodes == [
        "missing-target"
    ]
    