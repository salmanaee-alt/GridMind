from app.foundation.context import ExecutionContext
from app.foundation.validation import ExecutionContextValidator


def test_validator_accepts_default_context():
    context = ExecutionContext()

    result = ExecutionContextValidator().validate(
        context
    )

    assert result.valid is True