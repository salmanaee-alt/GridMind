from __future__ import annotations

from app.foundation.context import (
    ExecutionContext,
)
from app.foundation.metadata import (
    EngineMetadata,
)
from app.foundation.results import (
    EngineResult,
)
from app.foundation.types import (
    ExecutionStatus,
)
from app.graph.contracts import (
    EngineeringGraph,
)
from app.reasoning.confidence_contracts import (
    ConfidenceContribution,
    ConfidencePropagationResult,
)


CONFIDENCE_GRAPH_RESOURCE_KEY = (
    "confidence_graph"
)

CONFIDENCE_SCORES_RESOURCE_KEY = (
    "confidence_scores"
)


class ConfidencePropagationEngine:
    """
    Deterministic one-hop shadow confidence propagation engine.

    MVP v0.1 supports:
    - supports
    - contradicts

    It does not recursively propagate calculated scores.
    """

    @property
    def metadata(self) -> EngineMetadata:
        return EngineMetadata(
            name="confidence_propagation",
            version="0.1.0",
            description=(
                "Confidence propagation reasoning engine"
            ),
            category="reasoning",
            experimental=True,
        )

    def execute(
        self,
        context: ExecutionContext,
    ) -> EngineResult:
        graph = context.resources.get(
            CONFIDENCE_GRAPH_RESOURCE_KEY
        )

        confidence_scores = (
            context.resources.get(
                CONFIDENCE_SCORES_RESOURCE_KEY
            )
        )

        if (
            not isinstance(
                graph,
                EngineeringGraph,
            )
            or not isinstance(
                confidence_scores,
                dict,
            )
        ):
            return self._skipped_result()

        target_totals: dict[
            str,
            float,
        ] = {}

        contributions: list[
            ConfidenceContribution
        ] = []

        for edge in graph.edges:
            if edge.relation not in {
                "supports",
                "contradicts",
            }:
                continue

            if (
                edge.source_node_id
                not in confidence_scores
            ):
                continue

            incoming_confidence = (
                confidence_scores[
                    edge.source_node_id
                ]
            )

            if (
                not isinstance(
                    incoming_confidence,
                    (int, float),
                )
                or isinstance(
                    incoming_confidence,
                    bool,
                )
                or incoming_confidence < -1.0
                or incoming_confidence > 1.0
            ):
                continue

            incoming_confidence = float(
                incoming_confidence
            )

            edge_weight = 1.0
            attenuation = 1.0

            propagated_confidence = (
                incoming_confidence
                * edge_weight
                * attenuation
            )

            if edge.relation == "contradicts":
                propagated_confidence = (
                    -propagated_confidence
                )

            contributions.append(
                ConfidenceContribution(
                    source_node=(
                        edge.source_node_id
                    ),
                    target_node=(
                        edge.target_node_id
                    ),
                    relation=edge.relation,
                    incoming_confidence=(
                        incoming_confidence
                    ),
                    edge_weight=edge_weight,
                    attenuation=attenuation,
                    propagated_confidence=(
                        propagated_confidence
                    ),
                )
            )

            target_totals[
                edge.target_node_id
            ] = (
                target_totals.get(
                    edge.target_node_id,
                    0.0,
                )
                + propagated_confidence
            )

        propagated_scores = {
            target_node: max(
                -1.0,
                min(
                    1.0,
                    total,
                ),
            )
            for target_node, total
            in target_totals.items()
        }

        payload = ConfidencePropagationResult(
            propagated_scores=(
                propagated_scores
            ),
            contributions=tuple(
                contributions
            ),
        )

        return EngineResult(
            status=ExecutionStatus.SUCCESS,
            payload=payload,
            execution_summary=(
                "Confidence propagation completed "
                "using deterministic one-hop "
                "shadow computation."
            ),
        )

    @staticmethod
    def _skipped_result() -> EngineResult:
        return EngineResult(
            status=ExecutionStatus.SKIPPED,
            payload=ConfidencePropagationResult(),
            execution_summary=(
                "Confidence propagation skipped because "
                "required confidence resources were "
                "not available."
            ),
        )