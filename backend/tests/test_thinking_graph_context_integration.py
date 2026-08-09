from app.brain.engineering_session import (
    EngineeringSession,
)

from app.thinking.session_adapter import (
    engineering_session_to_thinking_state,
)


def test_graph_context_contains_real_graphs():
    session = EngineeringSession()

    session.add_evidence(
        {
            "evidence_id": "e1",
            "evidence_type": "test_evidence",
            "category": "physics",
            "source": "unit_test",
            "confidence": 0.9,
        }
    )

    session.add_hypothesis(
        {
            "hypothesis": "internal_fault",
        }
    )

    state = engineering_session_to_thinking_state(
        session
    )

    assert (
        state.graph_context.shadow_only
        is True
    )
    
    assert (
        state.graph_context.evidence_graph
        is not None
    )

    assert (
        state.graph_context.lineage_graph
        is not None
    )

    assert (
        len(
            state.graph_context
            .evidence_graph.nodes
        )
        == 1
    )

    assert (
        len(
            state.graph_context
            .lineage_graph.nodes
        )
        == 2
    )