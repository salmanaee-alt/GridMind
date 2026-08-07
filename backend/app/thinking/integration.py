from __future__ import annotations

from app.brain.engineering_session import (
    EngineeringSession,
)
from app.thinking.default_pipeline import (
    build_default_thinking_engine,
)
from app.thinking.session_adapter import (
    engineering_session_to_thinking_state,
)


def run_shadow_thinking_pipeline(
    session: EngineeringSession,
) -> EngineeringSession:
    state = engineering_session_to_thinking_state(
        session,
    )

    result = (
        build_default_thinking_engine()
        .execute(state)
    )

    metadata = dict(session.metadata)

    metadata["thinking"] = {
        "current_stage": (
            result.current_stage.value
        ),
        "stage_history": [
            record.stage.value
            for record in result.stage_history
        ],
        "metadata": result.metadata,
        "shadow_only": result.shadow_only,
        "affects_reasoning": (
            result.affects_reasoning
        ),
        "affects_decision": (
            result.affects_decision
        ),
    }

    session.metadata = metadata

    return session