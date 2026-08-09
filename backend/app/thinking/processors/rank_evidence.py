from __future__ import annotations

from typing import Any

from app.thinking.contracts import (
    ThinkingStage,
    ThinkingState,
)


def _extract_confidence(
    evidence: Any,
) -> float | None:
    if not isinstance(evidence, dict):
        return None

    value = evidence.get("confidence")

    if isinstance(value, (int, float)):
        return float(value)

    return None


class RankEvidenceProcessor:
    stage = ThinkingStage.RANK_EVIDENCE

    def execute(
        self,
        state: ThinkingState,
    ) -> ThinkingState:
        evidence_graph = (
            state.graph_context.evidence_graph
        )

        graph_available = (
            evidence_graph is not None
            and bool(evidence_graph.nodes)
        )

        ranked: list[dict[str, Any]] = []
        unranked_count = 0

        for index, evidence in enumerate(
            state.evidence
        ):
            confidence = _extract_confidence(
                evidence
            )

            if confidence is None:
                unranked_count += 1
                continue

            ranked.append(
                {
                    "evidence_index": index,
                    "confidence": confidence,
                }
            )

        ranked.sort(
            key=lambda item: (
                -item["confidence"],
                item["evidence_index"],
            )
        )

        return state.model_copy(
            update={
                "metadata": {
                    **state.metadata,
                    "rank_evidence_stage": {
                        "evidence_count": len(
                            state.evidence
                        ),
                        "ranked_count": len(
                            ranked
                        ),
                        "unranked_count": (
                            unranked_count
                        ),
                        "ranking": tuple(
                            ranked
                        ),
                        "ranking_status": (
                            "available"
                            if ranked
                            else "insufficient_metadata"
                        ),
                        "graph_context_used": (
                            graph_available
                        ),
                        "graph_node_count": (
                            len(
                                evidence_graph.nodes
                            )
                            if evidence_graph
                            is not None
                            else 0
                        ),
                    },
                }
            }
        )