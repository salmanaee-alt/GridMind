from app.brain.engineering_session import (
    EngineeringSession,
)
from app.lineage.builder import (
    build_lineage_graph,
)
from app.lineage.contracts import (
    LineageNodeType,
)

from app.lineage.contracts import (
    LineageRelation,
)


def test_builds_empty_graph():
    session = EngineeringSession()

    graph = build_lineage_graph(session)

    assert graph.nodes == ()
    assert graph.edges == ()


def test_builds_evidence_node():
    session = EngineeringSession()

    session.add_evidence({"type": "physics"})

    graph = build_lineage_graph(session)

    assert len(graph.nodes) == 1
    assert graph.nodes[0].node_type == (
        LineageNodeType.EVIDENCE
    )


def test_builds_hypothesis_node():
    session = EngineeringSession()

    session.add_hypothesis(
        {"name": "Internal fault"}
    )

    graph = build_lineage_graph(session)

    assert len(graph.nodes) == 1
    assert graph.nodes[0].node_type == (
        LineageNodeType.HYPOTHESIS
    )


def test_builds_reasoning_node():
    session = EngineeringSession()

    session.add_reasoning_step(
        {"stage": "reason"}
    )

    graph = build_lineage_graph(session)

    assert len(graph.nodes) == 1
    assert graph.nodes[0].node_type == (
        LineageNodeType.REASONING_STEP
    )


def test_builds_decision_node():
    session = EngineeringSession()

    session.add_decision(
        {"decision": "investigate"}
    )

    graph = build_lineage_graph(session)

    assert len(graph.nodes) == 1
    assert graph.nodes[0].node_type == (
        LineageNodeType.DECISION
    )


def test_builds_all_node_types():
    session = EngineeringSession()

    session.add_evidence({})
    session.add_hypothesis({})
    session.add_reasoning_step({})
    session.add_decision({})

    graph = build_lineage_graph(session)

    assert len(graph.nodes) == 4
    assert graph.edges == ()


def test_builds_explicit_lineage_edge():
    session = EngineeringSession()

    session.add_evidence(
        {
            "display_name": "COMTRADE",
        }
    )

    session.add_hypothesis(
        {
            "hypothesis": "Internal fault",
            "lineage_references": (
                {
                    "target_node_id": "evidence:0",
                    "relation": "supports",
                    "rationale": (
                        "COMTRADE supports the hypothesis."
                    ),
                    "source": "reasoning_engine",
                },
            ),
        }
    )

    graph = build_lineage_graph(session)

    assert len(graph.nodes) == 2
    assert len(graph.edges) == 1

    edge = graph.edges[0]

    assert edge.source_node == "hypothesis:0"
    assert edge.target_node == "evidence:0"
    assert edge.relation == LineageRelation.SUPPORTS

    assert (
        edge.metadata["rationale"]
        == "COMTRADE supports the hypothesis."
    )

    assert (
        edge.metadata["source"]
        == "reasoning_engine"
    )


def test_ignores_unknown_lineage_target():
    session = EngineeringSession()

    session.add_hypothesis(
        {
            "hypothesis": "Internal fault",
            "lineage_references": (
                {
                    "target_node_id": "evidence:999",
                    "relation": "supports",
                    "rationale": "Invalid reference.",
                    "source": "reasoning_engine",
                },
            ),
        }
    )

    graph = build_lineage_graph(session)

    assert len(graph.nodes) == 1
    assert graph.edges == ()


def test_without_lineage_references_builds_no_edges():
    session = EngineeringSession()

    session.add_evidence(
        {
            "display_name": "COMTRADE",
        }
    )

    session.add_hypothesis(
        {
            "hypothesis": "Internal fault",
        }
    )

    graph = build_lineage_graph(session)

    assert len(graph.nodes) == 2
    assert graph.edges == ()