from pydantic import ValidationError
import pytest

from app.graph.contracts import (
    EngineeringGraph,
    GraphEdge,
    GraphNode,
)

from app.reasoning.confidence_contracts import (
    ConfidenceContribution,
    ConfidenceEdgeWeight,
    ConfidencePropagationRequest,
    ConfidencePropagationResult,
)


def test_confidence_contribution_contract():
    contribution = ConfidenceContribution(
        source_node="evidence:0",
        target_node="hypothesis:0",
        relation="supports",
        incoming_confidence=0.90,
        edge_weight=1.0,
        attenuation=1.0,
        propagated_confidence=0.90,
    )

    assert contribution.source_node == "evidence:0"
    assert contribution.target_node == "hypothesis:0"


def test_confidence_result_defaults():
    result = ConfidencePropagationResult()

    assert result.propagated_scores == {}
    assert result.contributions == ()


def test_confidence_request_accepts_valid_input():
    graph = EngineeringGraph(
        graph_id="confidence-request",
        nodes=(
            GraphNode(
                node_id="evidence:0",
                node_type="evidence",
            ),
            GraphNode(
                node_id="hypothesis:0",
                node_type="hypothesis",
            ),
        ),
        edges=(
            GraphEdge(
                source_node_id="evidence:0",
                target_node_id="hypothesis:0",
                relation="supports",
            ),
        ),
    )

    request = ConfidencePropagationRequest(
        graph=graph,
        confidence_scores={
            "evidence:0": 0.8,
        },
    )

    assert request.graph == graph
    assert request.confidence_scores == {
        "evidence:0": 0.8,
    }


@pytest.mark.parametrize(
    "invalid_score",
    [
        1.01,
        -1.01,
        True,
        False,
    ],
)
def test_confidence_request_rejects_invalid_scores(
    invalid_score,
):
    graph = EngineeringGraph(
        graph_id="confidence-request",
    )

    with pytest.raises(ValidationError):
        ConfidencePropagationRequest(
            graph=graph,
            confidence_scores={
                "evidence:0": invalid_score,
            },
        )


def test_confidence_request_is_immutable():
    request = ConfidencePropagationRequest(
        graph=EngineeringGraph(
            graph_id="confidence-request",
        ),
        confidence_scores={
            "evidence:0": 0.8,
        },
    )

    with pytest.raises(ValidationError):
        request.confidence_scores = {}


def test_confidence_request_forbids_extra_fields():
    with pytest.raises(ValidationError):
        ConfidencePropagationRequest(
            graph=EngineeringGraph(
                graph_id="confidence-request",
            ),
            confidence_scores={},
            unexpected=True,
        )


def test_confidence_edge_weight_accepts_valid_weight():
    weight = ConfidenceEdgeWeight(
        source_node="evidence:0",
        target_node="hypothesis:0",
        relation="supports",
        weight=0.75,
    )

    assert weight.weight == pytest.approx(0.75)


@pytest.mark.parametrize(
    "invalid_weight",
    [
        -0.01,
        1.01,
        True,
        False,
    ],
)
def test_confidence_edge_weight_rejects_invalid_weight(
    invalid_weight,
):
    with pytest.raises(ValidationError):
        ConfidenceEdgeWeight(
            source_node="evidence:0",
            target_node="hypothesis:0",
            relation="supports",
            weight=invalid_weight,
        )


def test_confidence_request_accepts_edge_weights():
    graph = EngineeringGraph(
        graph_id="confidence-request",
    )

    weight = ConfidenceEdgeWeight(
        source_node="evidence:0",
        target_node="hypothesis:0",
        relation="supports",
        weight=0.75,
    )

    request = ConfidencePropagationRequest(
        graph=graph,
        confidence_scores={},
        edge_weights=(
            weight,
        ),
    )

    assert request.edge_weights == (
        weight,
    )


def test_confidence_request_accepts_edge_weights():
    graph = EngineeringGraph(
        graph_id="confidence-request",
        nodes=(
            GraphNode(
                node_id="evidence:0",
                node_type="evidence",
            ),
            GraphNode(
                node_id="hypothesis:0",
                node_type="hypothesis",
            ),
        ),
        edges=(
            GraphEdge(
                source_node_id="evidence:0",
                target_node_id="hypothesis:0",
                relation="supports",
            ),
        ),
    )

    weight = ConfidenceEdgeWeight(
        source_node="evidence:0",
        target_node="hypothesis:0",
        relation="supports",
        weight=0.75,
    )

    request = ConfidencePropagationRequest(
        graph=graph,
        confidence_scores={},
        edge_weights=(
            weight,
        ),
    )

    assert request.edge_weights == (
        weight,
    )


def test_confidence_request_rejects_duplicate_edge_weights():
    graph = EngineeringGraph(
        graph_id="confidence-request",
    )

    with pytest.raises(ValidationError):
        ConfidencePropagationRequest(
            graph=graph,
            confidence_scores={},
            edge_weights=(
                ConfidenceEdgeWeight(
                    source_node="evidence:0",
                    target_node="hypothesis:0",
                    relation="supports",
                    weight=0.40,
                ),
                ConfidenceEdgeWeight(
                    source_node="evidence:0",
                    target_node="hypothesis:0",
                    relation="supports",
                    weight=0.80,
                ),
            ),
        )


def test_confidence_request_rejects_orphan_edge_weight():
    graph = EngineeringGraph(
        graph_id="confidence-request",
        nodes=(
            GraphNode(
                node_id="evidence:0",
                node_type="evidence",
            ),
            GraphNode(
                node_id="hypothesis:0",
                node_type="hypothesis",
            ),
        ),
        edges=(
            GraphEdge(
                source_node_id="evidence:0",
                target_node_id="hypothesis:0",
                relation="supports",
            ),
        ),
    )

    with pytest.raises(ValidationError):
        ConfidencePropagationRequest(
            graph=graph,
            confidence_scores={
                "evidence:0": 0.80,
            },
            edge_weights=(
                ConfidenceEdgeWeight(
                    source_node="evidence:9",
                    target_node="hypothesis:9",
                    relation="supports",
                    weight=0.50,
                ),
            ),
        )


def test_confidence_request_rejects_weight_with_wrong_relation():
    graph = EngineeringGraph(
        graph_id="confidence-request",
        nodes=(
            GraphNode(
                node_id="evidence:0",
                node_type="evidence",
            ),
            GraphNode(
                node_id="hypothesis:0",
                node_type="hypothesis",
            ),
        ),
        edges=(
            GraphEdge(
                source_node_id="evidence:0",
                target_node_id="hypothesis:0",
                relation="supports",
            ),
        ),
    )

    with pytest.raises(ValidationError):
        ConfidencePropagationRequest(
            graph=graph,
            confidence_scores={
                "evidence:0": 0.80,
            },
            edge_weights=(
                ConfidenceEdgeWeight(
                    source_node="evidence:0",
                    target_node="hypothesis:0",
                    relation="contradicts",
                    weight=0.50,
                ),
            ),
        )