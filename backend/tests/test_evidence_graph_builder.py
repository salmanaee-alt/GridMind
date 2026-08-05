from app.brain.evidence_contracts import (
    EngineeringEvidence,
    EvidenceCategory,
    EvidenceValidity,
)
from app.brain.evidence_graph_builder import (
    build_evidence_graph,
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
    