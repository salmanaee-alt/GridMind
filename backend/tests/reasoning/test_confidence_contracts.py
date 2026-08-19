from pydantic import ValidationError
import pytest

from app.graph.contracts import (
    EngineeringGraph,
    GraphEdge,
    GraphNode,
)

from app.reasoning.confidence_contracts import (
    ConfidenceContribution,
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