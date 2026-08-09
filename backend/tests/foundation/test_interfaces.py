from app.foundation.context import ExecutionContext
from app.foundation.interfaces import Engine
from app.foundation.metadata import EngineMetadata
from app.foundation.results import EngineResult
from app.foundation.types import ExecutionStatus


class DummyEngine:
    @property
    def metadata(self) -> EngineMetadata:
        return EngineMetadata(
            name="dummy",
            version="1.0",
            description="Dummy",
            category="test",
        )

    def execute(
        self,
        context: ExecutionContext,
    ) -> EngineResult:
        return EngineResult(
            status=ExecutionStatus.SUCCESS,
        )


def test_dummy_engine_contract():
    engine: Engine = DummyEngine()

    result = engine.execute(
        ExecutionContext()
    )

    assert result.status == ExecutionStatus.SUCCESS