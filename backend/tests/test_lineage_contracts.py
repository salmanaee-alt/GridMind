import pytest
from pydantic import ValidationError

from app.lineage.contracts import (
    LineageAudit,
    LineageEdge,
    LineageGraph,
    LineageNode,
    LineageNodeType,
    LineageReference,
    LineageRelation,
    LineageValidation,
)


def test_creates_lineage_node():
    node = LineageNode(
        node_id="evidence:comtrade",
        node_type=LineageNodeType.EVIDENCE,
        display_name="COMTRADE waveform",
    )

    assert node.node_id == "evidence:comtrade"
    assert node.node_type == LineageNodeType.EVIDENCE
    assert node.display_name == "COMTRADE waveform"
    assert node.metadata == {}
    assert node.shadow_only is True
    assert node.affects_reasoning is False
    assert node.affects_decision is False


def test_creates_lineage_edge():
    edge = LineageEdge(
        source_node="evidence:comtrade",
        target_node="hypothesis:internal_fault",
        relation=LineageRelation.SUPPORTS,
    )

    assert edge.source_node == "evidence:comtrade"
    assert edge.target_node == "hypothesis:internal_fault"
    assert edge.relation == LineageRelation.SUPPORTS
    assert edge.metadata == {}
    assert edge.shadow_only is True
    assert edge.affects_reasoning is False
    assert edge.affects_decision is False


def test_creates_lineage_graph():
    node = LineageNode(
        node_id="decision:1",
        node_type=LineageNodeType.DECISION,
        display_name="Engineering decision",
    )

    graph = LineageGraph(
        nodes=(node,),
    )

    assert len(graph.nodes) == 1
    assert graph.nodes[0] == node
    assert graph.edges == ()
    assert graph.shadow_only is True
    assert graph.affects_reasoning is False
    assert graph.affects_decision is False


def test_creates_lineage_audit():
    audit = LineageAudit(
        node_count=3,
        edge_count=2,
        max_depth=2,
        traceability_ratio=1.0,
        complete=True,
    )

    assert audit.node_count == 3
    assert audit.edge_count == 2
    assert audit.max_depth == 2
    assert audit.traceability_ratio == 1.0
    assert audit.complete is True
    assert audit.shadow_only is True
    assert audit.affects_reasoning is False
    assert audit.affects_decision is False


def test_creates_lineage_validation():
    validation = LineageValidation(
        valid=False,
        cycles=(("node:a", "node:b", "node:a"),),
        orphan_nodes=("node:c",),
        missing_source_nodes=("node:d",),
    )

    assert validation.valid is False
    assert validation.cycles == (
        ("node:a", "node:b", "node:a"),
    )
    assert validation.orphan_nodes == ("node:c",)
    assert validation.missing_source_nodes == ("node:d",)
    assert validation.shadow_only is True
    assert validation.affects_reasoning is False
    assert validation.affects_decision is False


def test_models_are_immutable():
    node = LineageNode(
        node_id="source:relay",
        node_type=LineageNodeType.SOURCE,
        display_name="Relay event report",
    )

    with pytest.raises(ValidationError):
        node.display_name = "Changed"


def test_models_reject_extra_fields():
    with pytest.raises(ValidationError):
        LineageNode(
            node_id="source:relay",
            node_type=LineageNodeType.SOURCE,
            display_name="Relay event report",
            unexpected=True,
        )


def test_node_rejects_blank_id():
    with pytest.raises(ValidationError):
        LineageNode(
            node_id="",
            node_type=LineageNodeType.SOURCE,
            display_name="Relay event report",
        )


def test_audit_rejects_invalid_traceability_ratio():
    with pytest.raises(ValidationError):
        LineageAudit(
            node_count=1,
            edge_count=0,
            max_depth=0,
            traceability_ratio=1.1,
            complete=False,
        )


def test_shadow_flags_cannot_be_changed():
    with pytest.raises(ValidationError):
        LineageGraph(
            shadow_only=False,
        )

    with pytest.raises(ValidationError):
        LineageGraph(
            affects_reasoning=True,
        )

    with pytest.raises(ValidationError):
        LineageGraph(
            affects_decision=True,
        )


def test_creates_explicit_lineage_reference():
    reference = LineageReference(
        target_node_id="evidence:0",
        relation=LineageRelation.SUPPORTS,
        rationale=(
            "The referenced evidence explicitly supports "
            "the engineering hypothesis."
        ),
        source="transformer_reasoning",
    )

    assert reference.target_node_id == "evidence:0"
    assert reference.relation == LineageRelation.SUPPORTS
    assert reference.rationale
    assert reference.source == "transformer_reasoning"
    assert reference.shadow_only is True
    assert reference.affects_reasoning is False
    assert reference.affects_decision is False


def test_lineage_reference_requires_rationale():
    with pytest.raises(ValidationError):
        LineageReference(
            target_node_id="evidence:0",
            relation=LineageRelation.SUPPORTS,
            rationale="",
            source="test",
        )