from __future__ import annotations

import pytest

from app.foundation.context import ExecutionContext
from app.foundation.interfaces import Engine
from app.foundation.types import ExecutionStatus
from app.thinking.contracts import (
    ThinkingStage,
    ThinkingState,
)
from app.thinking.default_pipeline import (
    build_default_thinking_engine,
)
from app.thinking.foundation_adapter import (
    THINKING_STATE_RESOURCE_KEY,
    ThinkingFoundationAdapter,
)
from app.thinking.engine import (
    EngineeringThinkingEngine,
)


def build_state() -> ThinkingState:
    return ThinkingState(
        session_id="SESSION-ADAPTER-0001",
        observations=(
            {
                "type": "relay_event",
            },
        ),
        evidence=(
            {
                "evidence_id": "e1",
                "confidence": 0.9,
            },
        ),
        hypotheses=(
            {
                "hypothesis": "internal_fault",
            },
        ),
        decisions=(
            {
                "decision": "investigate",
            },
        ),
    )


def build_adapter() -> ThinkingFoundationAdapter:
    return ThinkingFoundationAdapter(
        engine=build_default_thinking_engine(),
    )


def test_thinking_adapter_satisfies_engine_contract():
    engine: Engine = build_adapter()

    assert engine.metadata.name


def test_thinking_adapter_metadata():
    adapter = build_adapter()

    assert adapter.metadata.name == (
        "engineering_thinking"
    )
    assert adapter.metadata.category == (
        "thinking"
    )
    assert adapter.metadata.version


def test_thinking_adapter_success_mapping():
    adapter = build_adapter()

    result = adapter.execute(
        ExecutionContext(
            resources={
                THINKING_STATE_RESOURCE_KEY:
                    build_state(),
            }
        )
    )

    assert (
        result.status
        == ExecutionStatus.SUCCESS
    )

    assert isinstance(
        result.payload,
        dict,
    )

    assert (
        result.payload["current_stage"]
        == ThinkingStage.COMPLETED.value
    )

    assert (
        len(
            result.payload["stage_history"]
        )
        == 11
    )

    assert result.shadow_only is True
    assert result.affects_reasoning is False
    assert result.affects_decision is False

def test_thinking_adapter_projects_native_result():
    adapter = build_adapter()

    state = build_state()

    result = adapter.execute(
        ExecutionContext(
            resources={
                THINKING_STATE_RESOURCE_KEY:
                    state,
            }
        )
    )

    assert result.payload[
        "current_stage"
    ] == ThinkingStage.COMPLETED.value

    assert isinstance(
        result.payload["stage_history"],
        list,
    )

    assert isinstance(
        result.payload["metadata"],
        dict,
    )


def test_thinking_adapter_maps_traceability():
    adapter = build_adapter()

    result = adapter.execute(
        ExecutionContext(
            resources={
                THINKING_STATE_RESOURCE_KEY:
                    build_state(),
            }
        )
    )

    assert (
        "SESSION-ADAPTER-0001"
        in result.diagnostics.traceability
    )


def test_thinking_adapter_diagnostics_derive_from_history():
    adapter = build_adapter()

    result = adapter.execute(
        ExecutionContext(
            resources={
                THINKING_STATE_RESOURCE_KEY:
                    build_state(),
            }
        )
    )

    assert (
        result.diagnostics.processed_items
        == len(
            result.payload[
                "stage_history"
            ]
        )
    )

    assert (
        result.diagnostics.processed_items
        == 11
    )

def test_thinking_adapter_missing_state():
    adapter = build_adapter()

    with pytest.raises(Exception):
        adapter.execute(
            ExecutionContext()
        )


def test_thinking_adapter_rejects_wrong_resource_type():
    adapter = build_adapter()

    with pytest.raises(Exception):
        adapter.execute(
            ExecutionContext(
                resources={
                    THINKING_STATE_RESOURCE_KEY:
                        {"session_id": "wrong-type"},
                }
            )
        )


def test_thinking_adapter_preserves_input_state():
    adapter = build_adapter()

    state = build_state()
    before = state.model_dump()

    adapter.execute(
        ExecutionContext(
            resources={
                THINKING_STATE_RESOURCE_KEY:
                    state,
            }
        )
    )

    assert state.model_dump() == before


def test_thinking_adapter_does_not_authorize_execution():
    adapter = build_adapter()

    state = ThinkingState(
        session_id="SESSION-SAFETY-0001",
        decisions=(
            {
                "decision": "reenergize",
            },
        ),
    )

    result = adapter.execute(
        ExecutionContext(
            resources={
                THINKING_STATE_RESOURCE_KEY:
                    state,
            }
        )
    )

    assert result.shadow_only is True
    assert result.affects_reasoning is False
    assert result.affects_decision is False

    assert (
        result.payload[
            "metadata"
        ][
            "decide_stage"
        ][
            "execution_authorized"
        ]
        is False
    )


def test_thinking_adapter_stage_history_matches_native_pipeline():
    state = build_state()

    native_engine = build_default_thinking_engine()
    native_result = native_engine.execute(
        state
    )

    adapter = ThinkingFoundationAdapter(
        engine=build_default_thinking_engine(),
    )

    adapted_result = adapter.execute(
        ExecutionContext(
            resources={
                THINKING_STATE_RESOURCE_KEY:
                    state,
            }
        )
    )

    assert (
        adapted_result.payload[
            "stage_history"
        ]
        == [
            record.stage.value
            for record
            in native_result.stage_history
        ]
    )

    assert (
        adapted_result.payload[
            "current_stage"
        ]
        == native_result.current_stage.value
    )

    assert (
        adapted_result.payload[
            "metadata"
        ]
        == native_result.metadata
    )

class UnsafeThinkingEngine(
    EngineeringThinkingEngine
):
    def execute(
        self,
        state: ThinkingState,
    ):
        class UnsafeResult:
            session_id = state.session_id
            current_stage = ThinkingStage.COMPLETED
            stage_history = ()
            metadata = {}
            shadow_only = False
            affects_reasoning = True
            affects_decision = True

        return UnsafeResult()


def test_thinking_adapter_native_safety_violation_is_rejected():
    adapter = ThinkingFoundationAdapter(
        engine=UnsafeThinkingEngine(),
    )

    with pytest.raises(ValueError):
        adapter.execute(
            ExecutionContext(
                resources={
                    THINKING_STATE_RESOURCE_KEY:
                        build_state(),
                }
            )
        )
                    