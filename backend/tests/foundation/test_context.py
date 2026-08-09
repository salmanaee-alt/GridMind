from app.foundation.context import (
    ExecutionContext,
)


def test_execution_context_defaults():
    context = ExecutionContext()

    assert context.correlation_id
    assert context.resources == {}
    assert context.metadata == {}