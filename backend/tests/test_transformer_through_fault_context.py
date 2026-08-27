from pydantic import ValidationError
import pytest

from app.transformer.through_fault_context import (
    ThroughFaultContext,
)

from app.transformer.schemas import (
    TransformerDifferentialTripRequest,
)


def test_through_fault_context_accepts_explicit_sequence():
    context = ThroughFaultContext(
        upstream_protection_operated=True,
        downstream_protection_operated=True,
        transformer_breakers_opened=True,
        high_through_fault_current_detected=True,
    )

    assert context.upstream_protection_operated is True
    assert context.downstream_protection_operated is True
    assert context.transformer_breakers_opened is True
    assert context.high_through_fault_current_detected is True


def test_through_fault_context_defaults_to_unknown():
    context = ThroughFaultContext()

    assert context.upstream_protection_operated is None
    assert context.downstream_protection_operated is None
    assert context.transformer_breakers_opened is None
    assert context.high_through_fault_current_detected is None


def test_through_fault_context_is_shadow_only():
    context = ThroughFaultContext()

    assert context.shadow_only is True
    assert context.affects_reasoning is False
    assert context.affects_decision is False


def test_through_fault_context_forbids_extra_fields():
    with pytest.raises(ValidationError):
        ThroughFaultContext(
            invented_signal=True,
        )