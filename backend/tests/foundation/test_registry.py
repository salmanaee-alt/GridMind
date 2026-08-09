import pytest

from app.foundation.context import ExecutionContext
from app.foundation.exceptions import (
    EngineNotFoundError,
    EngineRegistrationError,
)
from app.foundation.metadata import EngineMetadata
from app.foundation.registry import EngineRegistry
from app.foundation.results import EngineResult
from app.foundation.types import ExecutionStatus


class DummyEngine:
    @property
    def metadata(self):
        return EngineMetadata(
            name="dummy",
            version="1.0",
            description="Dummy",
            category="test",
        )

    def execute(self, context: ExecutionContext):
        return EngineResult(
            status=ExecutionStatus.SUCCESS,
        )


def test_register_engine():
    registry = EngineRegistry()

    registry.register(
        DummyEngine()
    )

    assert registry.exists(
        "dummy"
    )


def test_duplicate_registration():
    registry = EngineRegistry()

    registry.register(
        DummyEngine()
    )

    with pytest.raises(
        EngineRegistrationError
    ):
        registry.register(
            DummyEngine()
        )


def test_missing_engine():
    registry = EngineRegistry()

    with pytest.raises(
        EngineNotFoundError
    ):
        registry.resolve(
            "missing"
        )