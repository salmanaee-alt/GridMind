from app.brain.engineering_session import (
    EngineeringSession,
)
from app.thinking.contracts import (
    ThinkingStage,
)
from app.thinking.default_pipeline import (
    build_default_thinking_engine,
)
from app.thinking.session_adapter import (
    engineering_session_to_thinking_state,
)


def test_builds_default_engine():
    engine = build_default_thinking_engine()

    assert len(engine.processors) == 11


def test_session_adapter_builds_thinking_state():
    session = EngineeringSession(
        title="Test investigation",
    )

    session.add_observation(
        {
            "type": "relay_event",
        }
    )

    session.add_evidence(
        {
            "evidence_id": "e1",
            "confidence": 0.9,
        }
    )

    session.add_hypothesis(
        {
            "hypothesis": "internal_fault",
        }
    )

    session.add_decision(
        {
            "decision": "investigate",
        }
    )

    state = (
        engineering_session_to_thinking_state(
            session
        )
    )

    assert state.session_id == session.session_id
    assert len(state.observations) == 1
    assert len(state.evidence) == 1
    assert len(state.hypotheses) == 1
    assert len(state.decisions) == 1

    assert (
        state.metadata["source"]
        == "engineering_session"
    )


def test_default_pipeline_runs_end_to_end():
    session = EngineeringSession()

    session.add_observation(
        {
            "type": "relay_event",
        }
    )

    session.add_evidence(
        {
            "evidence_id": "e1",
            "confidence": 0.8,
        }
    )

    session.add_hypothesis(
        {
            "hypothesis": "internal_fault",
        }
    )

    session.add_decision(
        {
            "decision": "investigate",
        }
    )

    state = (
        engineering_session_to_thinking_state(
            session
        )
    )

    engine = build_default_thinking_engine()

    result = engine.execute(state)

    assert result.current_stage == (
        ThinkingStage.COMPLETED
    )

    assert len(result.stage_history) == 11

    assert (
        result.metadata[
            "observe_stage"
        ]["has_observations"]
        is True
    )

    assert (
        result.metadata[
            "validate_stage"
        ]["has_evidence"]
        is True
    )

    assert (
        result.metadata[
            "hypothesize_stage"
        ]["has_hypotheses"]
        is True
    )

    assert (
        result.metadata[
            "decide_stage"
        ]["has_decisions"]
        is True
    )

    assert len(result.explanations) == 1

    assert result.shadow_only is True
    assert result.affects_reasoning is False
    assert result.affects_decision is False


def test_default_pipeline_does_not_modify_session():
    session = EngineeringSession()

    session.add_observation(
        {
            "type": "relay_event",
        }
    )

    original = session.to_dict()

    state = (
        engineering_session_to_thinking_state(
            session
        )
    )

    build_default_thinking_engine().execute(
        state
    )

    assert session.to_dict() == original


def test_pipeline_does_not_authorize_execution():
    session = EngineeringSession()

    session.add_decision(
        {
            "decision": "reenergize",
        }
    )

    state = (
        engineering_session_to_thinking_state(
            session
        )
    )

    result = (
        build_default_thinking_engine()
        .execute(state)
    )

    assert (
        result.metadata[
            "decide_stage"
        ]["execution_authorized"]
        is False
    )