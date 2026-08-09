from __future__ import annotations

from app.graph.algorithms.reachability import (
    find_reachable_nodes,
)
from app.graph.contracts import (
    EngineeringGraph,
    GraphEdge,
    GraphNode,
)
from app.thinking.contracts import (
    ThinkingStage,
    ThinkingState,
)


def _lineage_to_engineering_graph(
    state: ThinkingState,
) -> EngineeringGraph | None:
    lineage_graph = (
        state.graph_context.lineage_graph
    )

    if lineage_graph is None:
        return None

    return EngineeringGraph(
        graph_id="thinking-lineage",
        nodes=tuple(
            GraphNode(
                node_id=node.node_id,
                node_type=node.node_type.value,
                metadata={
                    "display_name": (
                        node.display_name
                    ),
                    **node.metadata,
                },
            )
            for node in lineage_graph.nodes
        ),
        edges=tuple(
            GraphEdge(
                source_node_id=edge.source_node,
                target_node_id=edge.target_node,
                relation=edge.relation.value,
                metadata=edge.metadata,
            )
            for edge in lineage_graph.edges
        ),
    )


def _build_traceability(
    state: ThinkingState,
) -> tuple[dict[str, object], ...]:
    graph = _lineage_to_engineering_graph(
        state
    )

    lineage_graph = (
        state.graph_context.lineage_graph
    )

    if (
        graph is None
        or lineage_graph is None
    ):
        return ()

    traces: list[dict[str, object]] = []

    decision_nodes = [
        node
        for node in lineage_graph.nodes
        if node.node_type.value == "decision"
    ]

    for decision_node in decision_nodes:
        reachable = find_reachable_nodes(
            graph,
            start_node_id=(
                decision_node.node_id
            ),
        )

        traces.append(
            {
                "decision_node": (
                    decision_node.node_id
                ),
                "reachable_nodes": (
                    reachable
                ),
                "reachable_count": (
                    len(reachable)
                ),
            }
        )

    return tuple(traces)


class ExplainProcessor:
    stage = ThinkingStage.EXPLAIN

    def execute(
        self,
        state: ThinkingState,
    ) -> ThinkingState:
        lineage_graph = (
            state.graph_context.lineage_graph
        )

        lineage_available = (
            lineage_graph is not None
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

        traceability = _build_traceability(
            state
        )

        explanation_summary = {
            "observation_count": len(
                state.observations
            ),
            "evidence_count": len(
                state.evidence
            ),
            "hypothesis_count": len(
                state.hypotheses
            ),
            "physics_check_count": len(
                state.physics_checks
            ),
            "safety_finding_count": len(
                state.safety_findings
            ),
            "decision_count": len(
                state.decisions
            ),
            "lineage_node_count": (
                lineage_node_count
            ),
            "lineage_edge_count": (
                lineage_edge_count
            ),
        }

        explanation_available = any(
            (
                len(state.observations),
                len(state.evidence),
                len(state.hypotheses),
                len(state.physics_checks),
                len(state.safety_findings),
                len(state.decisions),
            )
        )

        explanation_item = {
            "type": (
                "structured_engineering_summary"
            ),
            "summary": explanation_summary,
            "generated_by": (
                "thinking_engine"
            ),
            "free_text_generated": False,
            "lineage_context": {
                "available": (
                    lineage_available
                ),
                "node_count": (
                    lineage_node_count
                ),
                "edge_count": (
                    lineage_edge_count
                ),
                "traceability": (
                    traceability
                ),
                "advisory_only": True,
            },
        }

        explanations = state.explanations

        if explanation_available:
            explanations = (
                *state.explanations,
                explanation_item,
            )

        return state.model_copy(
            update={
                "explanations": explanations,
                "metadata": {
                    **state.metadata,
                    "explain_stage": {
                        "explanation_available": (
                            explanation_available
                        ),
                        "explanation_count": len(
                            explanations
                        ),
                        "free_text_generated": (
                            False
                        ),
                        "graph_context_used": (
                            lineage_available
                        ),
                        "lineage_node_count": (
                            lineage_node_count
                        ),
                        "lineage_edge_count": (
                            lineage_edge_count
                        ),
                        "traceability_count": (
                            len(traceability)
                        ),
                    },
                },
            }
        )