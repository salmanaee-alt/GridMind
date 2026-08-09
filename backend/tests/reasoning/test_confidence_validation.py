from app.reasoning.confidence_contracts import (
    ConfidencePropagationResult,
)

from app.reasoning.confidence_validation import (
    validate_confidence_result,
)


def test_validation_accepts_shadow_result():
    result = ConfidencePropagationResult()

    assert (
        validate_confidence_result(
            result
        )
        is True
    )