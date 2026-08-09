from app.foundation.metadata import EngineMetadata


def test_engine_metadata():
    metadata = EngineMetadata(
        name="engine",
        version="1.0.0",
        description="Test",
        category="foundation",
    )

    assert metadata.name == "engine"
    assert metadata.experimental is False
    assert metadata.tags == ()