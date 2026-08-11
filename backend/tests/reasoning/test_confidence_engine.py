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