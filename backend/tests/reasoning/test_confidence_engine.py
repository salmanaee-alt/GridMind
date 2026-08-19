import pytest

from app.graph.contracts import (
    EngineeringGraph,
    GraphEdge,
    GraphNode,
)

from app.foundation.context import ExecutionContext
from app.foundation.interfaces import Engine
from app.foundation.results import EngineResult
from app.foundation.types import ExecutionStatus
from app.reasoning.confidence_engine import (
    ConfidencePropagationEngine,
)
from app.reasoning.confidence_contracts import (
    ConfidencePropagationResult,
)


def test_confidence_engine_satisfies_engine_contract():
    engine: Engine = ConfidencePropagationEngine()

    result = engine.execute(
        ExecutionContext()
    )

    assert isinstance(
        result,
        EngineResult,
    )


def test_confidence_engine_metadata():
    engine = ConfidencePropagationEngine()

    assert engine.metadata.name == (
        "confidence_propagation"
    )
    assert engine.metadata.category == (
        "reasoning"
    )


def test_confidence_engine_skips_without_input():
    engine = ConfidencePropagationEngine()

    result = engine.execute(
        ExecutionContext()
    )

    assert result.status == ExecutionStatus.SKIPPED
    assert result.shadow_only is True
    assert result.affects_reasoning is False
    assert result.affects_decision is False


def test_confidence_engine_returns_domain_payload():
    engine = ConfidencePropagationEngine()

    result = engine.execute(
        ExecutionContext()
    )

    assert isinstance(
        result.payload,
        ConfidencePropagationResult,
    )

    assert result.payload.propagated_scores == {}
    assert result.payload.contributions == ()


CONFIDENCE_GRAPH_RESOURCE_KEY = "confidence_graph"
CONFIDENCE_SCORES_RESOURCE_KEY = "confidence_scores"


def build_graph(
    *,
    edges: tuple[GraphEdge, ...],
) -> EngineeringGraph:
    node_ids = {
        edge.source_node_id
        for edge in edges
    } | {
        edge.target_node_id
        for edge in edges
    }

    nodes = tuple(
        GraphNode(
            node_id=node_id,
            node_type=(
                "evidence"
                if node_id.startswith("evidence:")
                else "hypothesis"
            ),
        )
        for node_id in sorted(node_ids)
    )

    return EngineeringGraph(
        graph_id="confidence-test",
        nodes=nodes,
        edges=edges,
    )


def build_context(
    *,
    graph: EngineeringGraph | None = None,
    scores: dict[str, float] | None = None,
) -> ExecutionContext:
    resources = {}

    if graph is not None:
        resources[
            CONFIDENCE_GRAPH_RESOURCE_KEY
        ] = graph

    if scores is not None:
        resources[
            CONFIDENCE_SCORES_RESOURCE_KEY
        ] = scores

    return ExecutionContext(
        resources=resources,
    )


def test_confidence_propagation_supports_relation():
    graph = build_graph(
        edges=(
            GraphEdge(
                source_node_id="evidence:0",
                target_node_id="hypothesis:0",
                relation="supports",
            ),
        )
    )

    result = ConfidencePropagationEngine().execute(
        build_context(
            graph=graph,
            scores={
                "evidence:0": 0.80,
            },
        )
    )

    assert result.status == ExecutionStatus.SUCCESS

    payload = result.payload

    assert payload.propagated_scores[
        "hypothesis:0"
    ] == pytest.approx(0.80)

    assert len(payload.contributions) == 1

    contribution = payload.contributions[0]

    assert contribution.source_node == "evidence:0"
    assert contribution.target_node == "hypothesis:0"
    assert contribution.relation == "supports"
    assert contribution.incoming_confidence == pytest.approx(
        0.80
    )
    assert contribution.edge_weight == pytest.approx(1.0)
    assert contribution.attenuation == pytest.approx(1.0)
    assert contribution.propagated_confidence == pytest.approx(
        0.80
    )


def test_confidence_propagation_contradicts_relation():
    graph = build_graph(
        edges=(
            GraphEdge(
                source_node_id="evidence:0",
                target_node_id="hypothesis:0",
                relation="contradicts",
            ),
        )
    )

    result = ConfidencePropagationEngine().execute(
        build_context(
            graph=graph,
            scores={
                "evidence:0": 0.60,
            },
        )
    )

    assert result.status == ExecutionStatus.SUCCESS

    assert result.payload.propagated_scores[
        "hypothesis:0"
    ] == pytest.approx(-0.60)


def test_confidence_propagation_aggregates_multiple_contributions():
    graph = build_graph(
        edges=(
            GraphEdge(
                source_node_id="evidence:0",
                target_node_id="hypothesis:0",
                relation="supports",
            ),
            GraphEdge(
                source_node_id="evidence:1",
                target_node_id="hypothesis:0",
                relation="contradicts",
            ),
        )
    )

    result = ConfidencePropagationEngine().execute(
        build_context(
            graph=graph,
            scores={
                "evidence:0": 0.80,
                "evidence:1": 0.60,
            },
        )
    )

    assert result.payload.propagated_scores[
        "hypothesis:0"
    ] == pytest.approx(0.20)


def test_confidence_propagation_clamps_positive_aggregate():
    graph = build_graph(
        edges=(
            GraphEdge(
                source_node_id="evidence:0",
                target_node_id="hypothesis:0",
                relation="supports",
            ),
            GraphEdge(
                source_node_id="evidence:1",
                target_node_id="hypothesis:0",
                relation="supports",
            ),
        )
    )

    result = ConfidencePropagationEngine().execute(
        build_context(
            graph=graph,
            scores={
                "evidence:0": 0.80,
                "evidence:1": 0.70,
            },
        )
    )

    assert result.payload.propagated_scores[
        "hypothesis:0"
    ] == pytest.approx(1.0)


def test_confidence_propagation_clamps_negative_aggregate():
    graph = build_graph(
        edges=(
            GraphEdge(
                source_node_id="evidence:0",
                target_node_id="hypothesis:0",
                relation="contradicts",
            ),
            GraphEdge(
                source_node_id="evidence:1",
                target_node_id="hypothesis:0",
                relation="contradicts",
            ),
        )
    )

    result = ConfidencePropagationEngine().execute(
        build_context(
            graph=graph,
            scores={
                "evidence:0": 0.80,
                "evidence:1": 0.70,
            },
        )
    )

    assert result.payload.propagated_scores[
        "hypothesis:0"
    ] == pytest.approx(-1.0)


def test_confidence_propagation_ignores_edge_without_source_score():
    graph = build_graph(
        edges=(
            GraphEdge(
                source_node_id="evidence:0",
                target_node_id="hypothesis:0",
                relation="supports",
            ),
        )
    )

    result = ConfidencePropagationEngine().execute(
        build_context(
            graph=graph,
            scores={},
        )
    )

    assert result.status == ExecutionStatus.SUCCESS
    assert result.payload.propagated_scores == {}
    assert result.payload.contributions == ()


def test_confidence_propagation_ignores_unsupported_relation():
    graph = build_graph(
        edges=(
            GraphEdge(
                source_node_id="evidence:0",
                target_node_id="hypothesis:0",
                relation="related_to",
            ),
        )
    )

    result = ConfidencePropagationEngine().execute(
        build_context(
            graph=graph,
            scores={
                "evidence:0": 0.80,
            },
        )
    )

    assert result.status == ExecutionStatus.SUCCESS
    assert result.payload.propagated_scores == {}
    assert result.payload.contributions == ()


def test_confidence_propagation_is_one_hop_only():
    graph = build_graph(
        edges=(
            GraphEdge(
                source_node_id="evidence:0",
                target_node_id="hypothesis:0",
                relation="supports",
            ),
            GraphEdge(
                source_node_id="hypothesis:0",
                target_node_id="hypothesis:1",
                relation="supports",
            ),
        )
    )

    result = ConfidencePropagationEngine().execute(
        build_context(
            graph=graph,
            scores={
                "evidence:0": 0.80,
            },
        )
    )

    assert result.payload.propagated_scores[
        "hypothesis:0"
    ] == pytest.approx(0.80)

    assert "hypothesis:1" not in (
        result.payload.propagated_scores
    )


def test_confidence_propagation_does_not_mutate_inputs():
    graph = build_graph(
        edges=(
            GraphEdge(
                source_node_id="evidence:0",
                target_node_id="hypothesis:0",
                relation="supports",
            ),
        )
    )

    scores = {
        "evidence:0": 0.80,
    }

    graph_before = graph.model_dump()
    scores_before = dict(scores)

    ConfidencePropagationEngine().execute(
        build_context(
            graph=graph,
            scores=scores,
        )
    )

    assert graph.model_dump() == graph_before
    assert scores == scores_before


def test_confidence_propagation_skips_when_graph_resource_missing():
    result = ConfidencePropagationEngine().execute(
        build_context(
            scores={
                "evidence:0": 0.80,
            },
        )
    )

    assert result.status == ExecutionStatus.SKIPPED


def test_confidence_propagation_skips_when_scores_resource_missing():
    graph = build_graph(
        edges=(
            GraphEdge(
                source_node_id="evidence:0",
                target_node_id="hypothesis:0",
                relation="supports",
            ),
        )
    )

    result = ConfidencePropagationEngine().execute(
        build_context(
            graph=graph,
        )
    )

    assert result.status == ExecutionStatus.SKIPPED


def test_confidence_propagation_preserves_authority_invariants_on_success():
    graph = build_graph(
        edges=(
            GraphEdge(
                source_node_id="evidence:0",
                target_node_id="hypothesis:0",
                relation="supports",
            ),
        )
    )

    result = ConfidencePropagationEngine().execute(
        build_context(
            graph=graph,
            scores={
                "evidence:0": 0.80,
            },
        )
    )

    assert result.status == ExecutionStatus.SUCCESS
    assert result.shadow_only is True
    assert result.affects_reasoning is False
    assert result.affects_decision is False


def test_confidence_propagation_clamps_after_full_aggregation():
    graph = build_graph(
        edges=(
            GraphEdge(
                source_node_id="evidence:0",
                target_node_id="hypothesis:0",
                relation="supports",
            ),
            GraphEdge(
                source_node_id="evidence:1",
                target_node_id="hypothesis:0",
                relation="supports",
            ),
            GraphEdge(
                source_node_id="evidence:2",
                target_node_id="hypothesis:0",
                relation="contradicts",
            ),
        )
    )

    result = ConfidencePropagationEngine().execute(
        build_context(
            graph=graph,
            scores={
                "evidence:0": 0.80,
                "evidence:1": 0.70,
                "evidence:2": 0.60,
            },
        )
    )

    assert result.payload.propagated_scores[
        "hypothesis:0"
    ] == pytest.approx(0.90)