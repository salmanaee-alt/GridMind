from __future__ import annotations

from app.thinking.contracts import (
    ThinkingStage,
    ThinkingState,
)


class UnderstandProcessor:
    stage = ThinkingStage.UNDERSTAND

    def execute(
        self,
        state: ThinkingState,
    ) -> ThinkingState:
        evidence_graph = (
            state.graph_context.evidence_graph
        )

        lineage_graph = (
            state.graph_context.lineage_graph
        )

        graph_context_available = (
            evidence_graph is not None
            or lineage_graph is not None
        )

        evidence_count = len(
            state.evidence
        )

        hypothesis_count = len(
            state.hypotheses
        )

        evidence_node_count = (
            len(evidence_graph.nodes)
            if evidence_graph is not None
            else 0
        )

        evidence_edge_count = (
            len(evidence_graph.edges)
            if evidence_graph is not None
            else 0
        )

        lineage_node_count = (
            len(lineage_graph.nodes)
            if lineage_graph is not None
            else 0
        )

        lineage_edge_count = (
            len(lineage_graph.edges)
            if lineage_graph is not None
            else 0
        )

        return state.model_copy(
            update={
                "metadata": {
                    **state.metadata,
                    "understand_stage": {
                        "evidence_count": (
                            evidence_count
                        ),
                        "hypothesis_count": (
                            hypothesis_count
                        ),
                        "has_engineering_context": (
                            bool(
                                state.observations
                                or state.evidence
                                or state.hypotheses
                            )
                        ),
                        "graph_context_used": (
                            graph_context_available
                        ),
                        "evidence_graph_nodes": (
                            evidence_node_count
                        ),
                        "evidence_graph_edges": (
                            evidence_edge_count
                        ),
                        "lineage_graph_nodes": (
                            lineage_node_count
                        ),
                        "lineage_graph_edges": (
                            lineage_edge_count
                        ),
                    },
                }
            }
        )