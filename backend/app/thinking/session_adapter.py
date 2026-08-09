from __future__ import annotations

from typing import Any

from app.brain.engineering_session import (
    EngineeringSession,
)
from app.brain.evidence_contracts import (
    EngineeringEvidence,
)
from app.brain.evidence_graph_builder import (
    build_evidence_graph,
)
from app.lineage.builder import (
    build_lineage_graph,
)
from app.thinking.contracts import (
    ThinkingState,
)
from app.thinking.graph_context import (
    ThinkingGraphContext,
)


def _as_tuple(
    value: list[Any],
) -> tuple[Any, ...]:
    return tuple(value)


def _to_engineering_evidence(
    item: Any,
) -> EngineeringEvidence | None:
    if isinstance(item, EngineeringEvidence):
        return item

    if isinstance(item, dict):
        try:
            return EngineeringEvidence.model_validate(
                item
            )
        except Exception:
            return None

    return None


def _build_session_evidence_graph(
    session: EngineeringSession,
):
    evidence_items = []

    for item in session.evidence:
        evidence = _to_engineering_evidence(
            item
        )

        if evidence is not None:
            evidence_items.append(
                evidence
            )

    return build_evidence_graph(
        evidence_items
    )


def engineering_session_to_thinking_state(
    session: EngineeringSession,
) -> ThinkingState:
    evidence_graph = (
        _build_session_evidence_graph(
            session
        )
    )

    lineage_graph = build_lineage_graph(
        session
    )

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
        graph_context=ThinkingGraphContext(
            evidence_graph=evidence_graph,
            lineage_graph=lineage_graph,
        ),
        metadata={
            "source": "engineering_session",
            "session_status": (
                session.status.value
            ),
        },
    )