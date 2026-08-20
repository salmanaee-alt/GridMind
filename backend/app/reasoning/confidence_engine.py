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
    ConfidenceEdgeWeight,
    ConfidencePropagationRequest,
    ConfidencePropagationResult,
)
from app.foundation.diagnostics import (
    EngineDiagnostics,
)


CONFIDENCE_REQUEST_RESOURCE_KEY = (
    "confidence_request"
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
        request = context.resources.get(
            CONFIDENCE_REQUEST_RESOURCE_KEY
        )

        if not isinstance(
            request,
            ConfidencePropagationRequest,
        ):
            return self._skipped_result()

        graph = request.graph
        confidence_scores = (
            request.confidence_scores
        )

        edge_weights = {
            (
                item.source_node,
                item.target_node,
                item.relation,
            ): item.weight
            for item in request.edge_weights
        }

        target_totals: dict[
            str,
            float,
        ] = {}

        contributions: list[
            ConfidenceContribution
        ] = []

        warnings: list[str] = []
        traceability: list[str] = []
        processed_items = 0
        skipped_items = 0

        for edge in graph.edges:
            if edge.relation not in {
                "supports",
                "contradicts",
            }:
                skipped_items += 1
                warnings.append(
                    "Skipped edge "
                    f"{edge.source_node_id!r} -> "
                    f"{edge.target_node_id!r}: "
                    f"unsupported relation {edge.relation!r}."
                )
                continue

            if (
                edge.source_node_id
                not in confidence_scores
            ):
                skipped_items += 1
                warnings.append(
                    "Skipped edge from "
                    f"{edge.source_node_id!r}: "
                    "missing source confidence."
                )
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
                skipped_items += 1
                warnings.append(
                    "Skipped edge from "
                    f"{edge.source_node_id!r}: "
                    "invalid source confidence."
                )
                continue

            incoming_confidence = float(
                incoming_confidence
            )

            edge_weight = edge_weights.get(
                (
                    edge.source_node_id,
                    edge.target_node_id,
                    edge.relation,
                ),
                1.0,
            )
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

            processed_items += 1

            if (
                edge.source_node_id
                not in traceability
            ):
                traceability.append(
                    edge.source_node_id
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

        total_edges = len(
            graph.edges
        )

        coverage = (
            1.0
            if total_edges == 0
            else processed_items / total_edges
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
            diagnostics=EngineDiagnostics(
                processed_items=(
                    processed_items
                ),
                skipped_items=(
                    skipped_items
                ),
                coverage=coverage,
                traceability=tuple(
                    traceability
                ),
                warnings=tuple(
                    warnings
                ),
            ),
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