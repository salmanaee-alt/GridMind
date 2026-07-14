import pytest

from app.knowledge.bootstrap import (
    build_default_registry,
)
from app.knowledge.context_builder import (
    build_knowledge_context,
)
from app.knowledge.registry import (
    EngineeringKnowledgeRegistry,
)
from app.knowledge.transformer import (
    INTERNAL_TRANSFORMER_FAULT,
    MAGNETIZING_INRUSH,
    TRANSFORMER_KNOWLEDGE,
)


def test_builder_creates_context_from_registry():
    registry = build_default_registry()

    context = build_knowledge_context(registry)

    assert context.schema_version == "1.0.0"
    assert context.shadow.enabled is True
    assert context.shadow.source == "registry"
    assert context.shadow.affects_decision is False


def test_builder_preserves_registry_order():
    registry = build_default_registry()

    context = build_knowledge_context(registry)

    assert tuple(
        item.knowledge_id
        for item in context.shadow.knowledge
    ) == tuple(
        item.knowledge_id
        for item in TRANSFORMER_KNOWLEDGE
    )


def test_builder_maps_knowledge_metadata_exactly():
    registry = build_default_registry()

    context = build_knowledge_context(registry)

    references = context.shadow.knowledge

    assert references[0].knowledge_id == (
        INTERNAL_TRANSFORMER_FAULT.knowledge_id
    )
    assert references[0].version == (
        INTERNAL_TRANSFORMER_FAULT.version
    )
    assert references[0].status == (
        INTERNAL_TRANSFORMER_FAULT.status
    )

    assert references[1].knowledge_id == (
        MAGNETIZING_INRUSH.knowledge_id
    )
    assert references[1].version == (
        MAGNETIZING_INRUSH.version
    )
    assert references[1].status == (
        MAGNETIZING_INRUSH.status
    )


def test_builder_returns_empty_context_for_empty_registry():
    registry = EngineeringKnowledgeRegistry()

    context = build_knowledge_context(registry)

    assert context.shadow.enabled is True
    assert context.shadow.knowledge == ()
    assert context.shadow.affects_decision is False


def test_builder_can_create_disabled_shadow_context():
    registry = build_default_registry()

    context = build_knowledge_context(
        registry,
        enabled=False,
    )

    assert context.shadow.enabled is False
    assert context.shadow.knowledge == ()
    assert context.shadow.affects_decision is False


def test_disabled_builder_does_not_expose_registry_knowledge():
    registry = build_default_registry()

    context = build_knowledge_context(
        registry,
        enabled=False,
    )

    assert context.shadow.knowledge == ()


def test_builder_does_not_mutate_registry():
    registry = build_default_registry()
    before = registry.all()

    build_knowledge_context(registry)

    assert registry.all() == before


def test_builder_rejects_non_registry_input():
    with pytest.raises(
        TypeError,
        match="EngineeringKnowledgeRegistry",
    ):
        build_knowledge_context(
            TRANSFORMER_KNOWLEDGE
        )


def test_builder_returns_new_context_each_time():
    registry = build_default_registry()

    first = build_knowledge_context(registry)
    second = build_knowledge_context(registry)

    assert first is not second
    assert first == second


def test_builder_preserves_exact_registered_scope():
    registry = EngineeringKnowledgeRegistry(
        (
            INTERNAL_TRANSFORMER_FAULT,
            MAGNETIZING_INRUSH,
        )
    )

    context = build_knowledge_context(registry)

    assert tuple(
        item.knowledge_id
        for item in context.shadow.knowledge
    ) == (
        "TR-EKO-0001",
        "TR-EKO-0002",
    )
