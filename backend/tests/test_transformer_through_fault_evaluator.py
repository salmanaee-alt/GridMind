from app.transformer.through_fault_context import (
    ThroughFaultContext,
)
from app.transformer.through_fault_evaluator import (
    evaluate_through_fault_context,
)


def test_through_fault_is_supported_with_complete_sequence():
    result = evaluate_through_fault_context(
        ThroughFaultContext(
            upstream_protection_operated=True,
            downstream_protection_operated=True,
            transformer_breakers_opened=True,
            high_through_fault_current_detected=True,
        )
    )

    assert result.status == "supported"
    assert result.confirmed is False
    assert result.shadow_only is True
    assert result.affects_reasoning is False
    assert result.affects_decision is False


def test_through_fault_is_not_supported_when_sequence_is_negative():
    result = evaluate_through_fault_context(
        ThroughFaultContext(
            upstream_protection_operated=False,
            downstream_protection_operated=False,
            transformer_breakers_opened=False,
            high_through_fault_current_detected=False,
        )
    )

    assert result.status == "not_supported"
    assert result.confirmed is False


def test_through_fault_is_insufficient_without_context():
    result = evaluate_through_fault_context(
        ThroughFaultContext()
    )

    assert result.status == "insufficient_evidence"
    assert result.confirmed is False


def test_single_through_fault_indicator_is_insufficient():
    result = evaluate_through_fault_context(
        ThroughFaultContext(
            high_through_fault_current_detected=True,
        )
    )

    assert result.status == "insufficient_evidence"
    assert result.confirmed is False