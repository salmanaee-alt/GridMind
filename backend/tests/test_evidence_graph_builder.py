from app.brain.evidence_contracts import (
    EngineeringEvidence,
    EvidenceCategory,
    EvidenceRelationship,
    EvidenceRelationshipType,
    EvidenceValidity,
)
from app.brain.evidence_graph_builder import (
    build_evidence_graph,
)

from app.brain.evidence_graph_contracts import (
    EvidenceRelation,
)

def test_builds_empty_graph_from_empty_evidence():
    graph = build_evidence_graph([])

    assert graph.nodes == []
    assert graph.edges == []
    assert graph.shadow_only is True
    assert graph.affects_reasoning is False
    assert graph.affects_decision is False


def test_builds_node_from_engineering_evidence():
    evidence = EngineeringEvidence(
        evidence_id="physics:differential_current",
        evidence_type="differential_current",
        category=EvidenceCategory.PHYSICS,
        source="transformer_physics",
        value={
            "phase_a_diff_a": 5.1,
        },
        validity=EvidenceValidity.VALID,
    )

    graph = build_evidence_graph([evidence])

    assert len(graph.nodes) == 1
    assert graph.edges == []

    node = graph.nodes[0]

    assert node.node_id == (
        "evidence-node:physics:differential_current"
    )
    assert node.evidence_id == (
        "physics:differential_current"
    )
    assert node.evidence_type == (
        "differential_current"
    )
    assert node.category == "physics"


def test_builds_one_node_per_evidence_item():
    evidence_items = [
        EngineeringEvidence(
            evidence_id="physics:differential_current",
            evidence_type="differential_current",
            category=EvidenceCategory.PHYSICS,
            source="transformer_physics",
            validity=EvidenceValidity.VALID,
        ),
        EngineeringEvidence(
            evidence_id="physics:harmonic_restraint",
            evidence_type="harmonic_restraint",
            category=EvidenceCategory.PHYSICS,
            source="transformer_physics",
            validity=EvidenceValidity.VALID,
        ),
    ]

    graph = build_evidence_graph(evidence_items)

    assert len(graph.nodes) == 2
    assert graph.edges == []

    evidence_ids = {
        node.evidence_id
        for node in graph.nodes
    }

    assert evidence_ids == {
        "physics:differential_current",
        "physics:harmonic_restraint",
    }


def test_builds_edge_from_explicit_relationship():
    source = EngineeringEvidence(
        evidence_id="physics:differential_current",
        evidence_type="differential_current",
        category=EvidenceCategory.PHYSICS,
        source="transformer_physics",
        validity=EvidenceValidity.VALID,
        relationships=(
            EvidenceRelationship(
                target_evidence_id="measurement:hv_current",
                relation=(
                    EvidenceRelationshipType.DERIVED_FROM
                ),
                source="transformer_physics_adapter",
                rationale=(
                    "The differential current is derived from the "
                    "high-voltage current measurement."
                ),
            ),
        ),
    )

    target = EngineeringEvidence(
        evidence_id="measurement:hv_current",
        evidence_type="hv_current",
        category=EvidenceCategory.MEASUREMENT,
        source="comtrade",
        validity=EvidenceValidity.VALID,
    )

    graph = build_evidence_graph(
        [source, target]
    )

    assert len(graph.edges) == 1

    edge = graph.edges[0]

    assert (
        edge.source_node
        == "evidence-node:physics:differential_current"
    )
    assert (
        edge.target_node
        == "evidence-node:measurement:hv_current"
    )
    assert edge.relation == EvidenceRelation.DERIVED_FROM


def test_does_not_create_edge_for_missing_target():
    source = EngineeringEvidence(
        evidence_id="physics:differential_current",
        evidence_type="differential_current",
        category=EvidenceCategory.PHYSICS,
        source="transformer_physics",
        relationships=(
            EvidenceRelationship(
                target_evidence_id="measurement:missing",
                relation=(
                    EvidenceRelationshipType.DERIVED_FROM
                ),
                source="transformer_physics_adapter",
                rationale=(
                    "The differential current is derived from the "
                    "high-voltage current measurement."
                )
            ),
        ),
    )

    graph = build_evidence_graph([source])

    assert len(graph.nodes) == 1
    assert graph.edges == []


def test_provenance_inputs_do_not_create_relationships():
    source = EngineeringEvidence(
        evidence_id="physics:differential_current",
        evidence_type="differential_current",
        category=EvidenceCategory.PHYSICS,
        source="transformer_physics",
        provenance={
            "inputs": [
                "measurement:hv_current",
                "measurement:lv_current",
            ],
        },
    )

    hv_target = EngineeringEvidence(
        evidence_id="measurement:hv_current",
        evidence_type="hv_current",
        category=EvidenceCategory.MEASUREMENT,
        source="comtrade",
    )

    lv_target = EngineeringEvidence(
        evidence_id="measurement:lv_current",
        evidence_type="lv_current",
        category=EvidenceCategory.MEASUREMENT,
        source="comtrade",
    )

    graph = build_evidence_graph(
        [source, hv_target, lv_target]
    )

    assert len(graph.nodes) == 3
    assert graph.edges == []
