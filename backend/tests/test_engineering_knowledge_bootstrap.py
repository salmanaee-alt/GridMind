from app.knowledge.bootstrap import (
    build_default_registry,
)
from app.knowledge.transformer import (
    INTERNAL_TRANSFORMER_FAULT,
    TRANSFORMER_KNOWLEDGE,
)


def test_default_registry_contains_transformer_knowledge():
    registry = build_default_registry()

    assert registry.all() == TRANSFORMER_KNOWLEDGE
    assert registry.get("TR-EKO-0001") is (
        INTERNAL_TRANSFORMER_FAULT
    )


def test_default_registry_build_is_deterministic():
    first = build_default_registry()
    second = build_default_registry()

    assert first.all() == second.all()
    assert first.all() == TRANSFORMER_KNOWLEDGE


def test_default_registry_build_returns_independent_registries():
    first = build_default_registry()
    second = build_default_registry()

    assert first is not second

    first.register(
        TRANSFORMER_KNOWLEDGE[0].model_copy(
            update={
                "knowledge_id": "TR-EKO-9999",
                "title": "Temporary Test Knowledge",
            }
        )
    )

    assert first.exists("TR-EKO-9999") is True
    assert second.exists("TR-EKO-9999") is False


def test_default_registry_preserves_registration_order():
    registry = build_default_registry()

    assert registry.all() == TRANSFORMER_KNOWLEDGE
