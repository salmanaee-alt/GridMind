from __future__ import annotations

from typing import Any

from app.thinking.contracts import (
    ThinkingStage,
    ThinkingState,
)


def _extract_candidate(
    item: Any,
    *,
    source_type: str,
    source_index: int,
) -> dict[str, Any] | None:
    if not isinstance(item, dict):
        return None

    if not item:
        return None

    return {
        "source_type": source_type,
        "source_index": source_index,
        "content": item,
        "review_required": True,
        "memory_write_authorized": False,
    }


class LearnProcessor:
    stage = ThinkingStage.LEARN

    def execute(
        self,
        state: ThinkingState,
    ) -> ThinkingState:
        candidates: list[
            dict[str, Any]
        ] = []

        collections = (
            (
                "decision",
                state.decisions,
            ),
            (
                "explanation",
                state.explanations,
            ),
            (
                "safety_finding",
                state.safety_findings,
            ),
        )

        for source_type, items in collections:
            for index, item in enumerate(items):
                candidate = _extract_candidate(
                    item,
                    source_type=source_type,
                    source_index=index,
                )

                if candidate is not None:
                    candidates.append(
                        candidate
                    )

        learning_items = (
            *state.learning_items,
            *candidates,
        )

        return state.model_copy(
            update={
                "learning_items": (
                    learning_items
                ),
                "metadata": {
                    **state.metadata,
                    "learn_stage": {
                        "candidate_count": len(
                            candidates
                        ),
                        "learning_item_count": (
                            len(learning_items)
                        ),
                        "review_required": True,
                        "memory_write_authorized": (
                            False
                        ),
                        "learning_status": (
                            "candidates_available"
                            if candidates
                            else "no_candidates"
                        ),
                    },
                },
            }
        )