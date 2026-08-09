from app.foundation.types import ExecutionStatus


def test_execution_status_values():
    assert ExecutionStatus.SUCCESS.value == "success"
    assert ExecutionStatus.FAILED.value == "failed"
    assert ExecutionStatus.PARTIAL.value == "partial"
    assert ExecutionStatus.SKIPPED.value == "skipped"