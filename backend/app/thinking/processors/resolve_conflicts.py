from __future__ import annotations

from typing import Any

from app.thinking.contracts import (
    ThinkingStage,
    ThinkingState,
)


def _extract_conflicts(
    item: Any,
) -> tuple[Any, ...]:
    if not isinstance(item, dict):
        return ()

    raw_conflicts = item.get(
        "conflicts",
        (),
    )

    if raw_conflicts is None:
        return ()

    if isinstance(raw_conflicts, tuple):
        return raw_conflicts

    if isinstance(raw_conflicts, list):
        return tuple(raw_conflicts)

    return (raw_conflicts,)


class ResolveConflictsProcessor:
    stage = ThinkingStage.RESOLVE_CONFLICTS

    def execute(
        self,
        state: ThinkingState,
    ) -> ThinkingState:
        evidence_graph = (
            state.graph_context.evidence_graph
        )

        graph_conflicts: list[
            dict[str, Any]
        ] = []

        if evidence_graph is not None:
            for edge in evidence_graph.edges:
                if edge.relation.value not in {
                    "contradicts",
                    "invalidates",
                }:
                    continue

                graph_conflicts.append(
                    {
                        "source_node": (
                            edge.source_node
                        ),
                        "target_node": (
                            edge.target_node
                        ),
                        "relation": (
                            edge.relation.value
                        ),
                    }
                )

        conflicts: list[
            dict[str, Any]
        ] = []

        for index, evidence in enumerate(
            state.evidence
        ):
            for conflict in _extract_conflicts(
                evidence
            ):
                conflicts.append(
                    {
                        "source_type": "evidence",
                        "source_index": index,
                        "conflict": conflict,
                    }
                )

        for index, hypothesis in enumerate(
            state.hypotheses
        ):
            for conflict in _extract_conflicts(
                hypothesis
            ):
                conflicts.append(
                    {
                        "source_type": (
                            "hypothesis"
                        ),
                        "source_index": index,
                        "conflict": conflict,
                    }
                )

        return state.model_copy(
            update={
                "metadata": {
                    **state.metadata,
                    "resolve_conflicts_stage": {
                        "conflict_count": len(
                            conflicts
                        ),
                        "has_conflicts": bool(
                            conflicts
                        ),
                        "conflicts": tuple(
                            conflicts
                        ),
                        "resolution_status": (
                            "requires_review"
                            if conflicts
                            else "no_conflicts"
                        ),
                        "graph_context_used": (
                            evidence_graph
                            is not None
                        ),
                        "graph_conflict_count": (
                            len(graph_conflicts)
                        ),
                        "graph_conflicts": tuple(
                            graph_conflicts
                        ),
                    },
                }
            }
        )