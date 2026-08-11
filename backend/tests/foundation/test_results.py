import pytest
from pydantic import ValidationError

from app.foundation.results import EngineResult
from app.foundation.types import ExecutionStatus


def test_engine_result_defaults():
    result = EngineResult(
        status=ExecutionStatus.SUCCESS,
    )

    assert result.shadow_only is True
    assert result.affects_reasoning is False
    assert result.affects_decision is False


def test_engine_result_rejects_authoritative_flags():
    with pytest.raises(ValidationError):
        EngineResult(
            status=ExecutionStatus.SUCCESS,
            affects_decision=True,
        )

    with pytest.raises(ValidationError):
        EngineResult(
            status=ExecutionStatus.SUCCESS,
            affects_reasoning=True,
        )

    with pytest.raises(ValidationError):
        EngineResult(
            status=ExecutionStatus.SUCCESS,
            shadow_only=False,
        )