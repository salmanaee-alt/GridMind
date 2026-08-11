from app.reasoning.confidence_contracts import (
    ConfidenceContribution,
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
