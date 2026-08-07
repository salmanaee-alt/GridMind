from app.brain.engineering_session import (
    EngineeringSession,
)
from app.thinking.integration import (
    run_shadow_thinking_pipeline,
)


def test_shadow_pipeline_adds_metadata():
    session = EngineeringSession()

    session.add_observation(
        {
            "type": "relay_event",
        }
    )

    session = run_shadow_thinking_pipeline(
        session,
    )

    assert "thinking" in session.metadata

    thinking = session.metadata["thinking"]

    assert thinking["shadow_only"] is True
    assert (
        thinking["affects_reasoning"]
        is False
    )
    assert (
        thinking["affects_decision"]
        is False
    )


def test_shadow_pipeline_keeps_existing_metadata():
    session = EngineeringSession()

    session.metadata["source"] = "unit_test"

    session = run_shadow_thinking_pipeline(
        session,
    )

    assert (
        session.metadata["source"]
        == "unit_test"
    )

    assert "thinking" in session.metadata


def test_shadow_pipeline_records_completed_stage():
    session = EngineeringSession()

    session = run_shadow_thinking_pipeline(
        session,
    )

    thinking = session.metadata["thinking"]

    assert (
        thinking["current_stage"]
        == "completed"
    )

    assert len(
        thinking["stage_history"]
    ) == 11