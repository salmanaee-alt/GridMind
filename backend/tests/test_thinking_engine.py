from app.thinking.contracts import (
    ThinkingStage,
    ThinkingState,
)
from app.thinking.engine import (
    EngineeringThinkingEngine,
)


def test_empty_engine_completes_pipeline():
    state = ThinkingState(
        session_id="session-1",
    )

    engine = EngineeringThinkingEngine()

    result = engine.execute(state)

    assert result.current_stage == (
        ThinkingStage.COMPLETED
    )

    assert len(result.stage_history) == 11


def test_pipeline_stage_order_is_stable():
    state = ThinkingState(
        session_id="session-1",
    )

    result = EngineeringThinkingEngine().execute(
        state
    )

    assert tuple(
        record.stage
        for record in result.stage_history
    ) == (
        ThinkingStage.OBSERVE,
        ThinkingStage.UNDERSTAND,
        ThinkingStage.VALIDATE,
        ThinkingStage.HYPOTHESIZE,
        ThinkingStage.RANK_EVIDENCE,
        ThinkingStage.RESOLVE_CONFLICTS,
        ThinkingStage.VERIFY_PHYSICS,
        ThinkingStage.SAFETY_GATE,
        ThinkingStage.DECIDE,
        ThinkingStage.EXPLAIN,
        ThinkingStage.LEARN,
    )


def test_all_stage_records_are_completed():
    state = ThinkingState(
        session_id="session-1",
    )

    result = EngineeringThinkingEngine().execute(
        state
    )

    assert all(
        record.completed
        for record in result.stage_history
    )


def test_original_state_remains_unchanged():
    state = ThinkingState(
        session_id="session-1",
    )

    EngineeringThinkingEngine().execute(state)

    assert state.current_stage == (
        ThinkingStage.OBSERVE
    )

    assert state.stage_history == ()


def test_processor_can_update_state():
    class ObserveProcessor:
        stage = ThinkingStage.OBSERVE

        def execute(
            self,
            state: ThinkingState,
        ) -> ThinkingState:
            return state.model_copy(
                update={
                    "observations": (
                        *state.observations,
                        {
                            "type": "test_observation",
                        },
                    )
                }
            )

    state = ThinkingState(
        session_id="session-1",
    )

    engine = EngineeringThinkingEngine(
        processors=(
            ObserveProcessor(),
        )
    )

    result = engine.execute(state)

    assert result.observations == (
        {
            "type": "test_observation",
        },
    )


def test_processor_only_runs_for_its_stage():
    calls: list[str] = []

    class ValidateProcessor:
        stage = ThinkingStage.VALIDATE

        def execute(
            self,
            state: ThinkingState,
        ) -> ThinkingState:
            calls.append(
                self.stage.value
            )
            return state

    state = ThinkingState(
        session_id="session-1",
    )

    engine = EngineeringThinkingEngine(
        processors=(
            ValidateProcessor(),
        )
    )

    engine.execute(state)

    assert calls == [
        "validate",
    ]


def test_pipeline_remains_shadow_only():
    state = ThinkingState(
        session_id="session-1",
    )

    result = EngineeringThinkingEngine().execute(
        state
    )

    assert result.shadow_only is True
    assert result.affects_reasoning is False
    assert result.affects_decision is False