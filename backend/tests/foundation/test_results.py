from app.foundation.results import EngineResult
from app.foundation.types import ExecutionStatus


def test_engine_result_defaults():
    result = EngineResult(
        status=ExecutionStatus.SUCCESS,
    )

    assert result.shadow_only is True
    assert result.affects_reasoning is False
    assert result.affects_decision is False