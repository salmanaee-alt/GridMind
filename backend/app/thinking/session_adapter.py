from __future__ import annotations

from typing import Any

from app.brain.engineering_session import (
    EngineeringSession,
)
from app.thinking.contracts import (
    ThinkingState,
)


def _as_tuple(
    value: list[Any],
) -> tuple[Any, ...]:
    return tuple(value)


def engineering_session_to_thinking_state(
    session: EngineeringSession,
) -> ThinkingState:
    return ThinkingState(
        session_id=session.session_id,
        observations=_as_tuple(
            session.observations
        ),
        evidence=_as_tuple(
            session.evidence
        ),
        hypotheses=_as_tuple(
            session.hypotheses
        ),
        decisions=_as_tuple(
            session.decisions
        ),
        metadata={
            "source": "engineering_session",
            "session_status": (
                session.status.value
            ),
        },
    )