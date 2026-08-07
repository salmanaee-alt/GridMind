import pytest
from pydantic import ValidationError

from app.thinking.contracts import (
    ThinkingStage,
    ThinkingStageRecord,
    ThinkingState,
)


def test_creates_thinking_state():
    state = ThinkingState(
        session_id="session-1",
    )

    assert state.session_id == "session-1"
    assert state.current_stage == ThinkingStage.OBSERVE

    assert state.observations == ()
    assert state.evidence == ()
    assert state.hypotheses == ()
    assert state.physics_checks == ()
    assert state.safety_findings == ()
    assert state.decisions == ()
    assert state.explanations == ()
    assert state.learning_items == ()
    assert state.stage_history == ()

    assert state.shadow_only is True
    assert state.affects_reasoning is False
    assert state.affects_decision is False


def test_creates_stage_record():
    record = ThinkingStageRecord(
        stage=ThinkingStage.VALIDATE,
        completed=True,
        summary="Evidence validation completed.",
        data={
            "evidence_count": 3,
        },
    )

    assert record.stage == ThinkingStage.VALIDATE
    assert record.completed is True

    assert record.data == {
        "evidence_count": 3,
    }


def test_supports_all_thinking_stages():
    expected = {
        "observe",
        "understand",
        "validate",
        "hypothesize",
        "rank_evidence",
        "resolve_conflicts",
        "verify_physics",
        "safety_gate",
        "decide",
        "explain",
        "learn",
        "completed",
    }

    assert {
        stage.value
        for stage in ThinkingStage
    } == expected


def test_state_accepts_engineering_data():
    state = ThinkingState(
        session_id="session-1",
        current_stage=ThinkingStage.HYPOTHESIZE,
        observations=(
            {
                "type": "relay_event",
            },
        ),
        evidence=(
            {
                "evidence_id": "e1",
            },
        ),
        hypotheses=(
            {
                "hypothesis": "internal_fault",
            },
        ),
    )

    assert len(state.observations) == 1
    assert len(state.evidence) == 1
    assert len(state.hypotheses) == 1


def test_state_is_immutable():
    state = ThinkingState(
        session_id="session-1",
    )

    with pytest.raises(ValidationError):
        state.current_stage = ThinkingStage.DECIDE


def test_stage_record_is_immutable():
    record = ThinkingStageRecord(
        stage=ThinkingStage.OBSERVE,
    )

    with pytest.raises(ValidationError):
        record.completed = True


def test_state_rejects_extra_fields():
    with pytest.raises(ValidationError):
        ThinkingState(
            session_id="session-1",
            unexpected=True,
        )


def test_state_rejects_blank_session_id():
    with pytest.raises(ValidationError):
        ThinkingState(
            session_id="",
        )


def test_shadow_flags_cannot_be_changed():
    with pytest.raises(ValidationError):
        ThinkingState(
            session_id="session-1",
            shadow_only=False,
        )

    with pytest.raises(ValidationError):
        ThinkingState(
            session_id="session-1",
            affects_reasoning=True,
        )

    with pytest.raises(ValidationError):
        ThinkingState(
            session_id="session-1",
            affects_decision=True,
        )