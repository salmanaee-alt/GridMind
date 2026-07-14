import pytest

from app.knowledge.registry import (
    EngineeringKnowledgeRegistry,
)
from app.knowledge.transformer import (
    INTERNAL_TRANSFORMER_FAULT,
    MAGNETIZING_INRUSH,
    TRANSFORMER_KNOWLEDGE,
)


def test_registry_starts_empty():
    registry = EngineeringKnowledgeRegistry()

    assert registry.all() == ()
    assert registry.exists("TR-EKO-0001") is False
    assert registry.get("TR-EKO-0001") is None


def test_registry_registers_and_retrieves_knowledge():
    registry = EngineeringKnowledgeRegistry()

    registry.register(INTERNAL_TRANSFORMER_FAULT)

    assert registry.exists("TR-EKO-0001") is True
    assert registry.get("TR-EKO-0001") is (
        INTERNAL_TRANSFORMER_FAULT
    )


def test_registry_rejects_duplicate_knowledge_id():
    registry = EngineeringKnowledgeRegistry()

    registry.register(INTERNAL_TRANSFORMER_FAULT)

    with pytest.raises(
        ValueError,
        match="already registered",
    ):
        registry.register(INTERNAL_TRANSFORMER_FAULT)


def test_registry_rejects_non_knowledge_objects():
    registry = EngineeringKnowledgeRegistry()

    with pytest.raises(
        TypeError,
        match="EngineeringKnowledgeObject",
    ):
        registry.register(
            {
                "knowledge_id": "TR-EKO-9999",
            }
        )


def test_registry_all_preserves_registration_order():
    registry = EngineeringKnowledgeRegistry()

    registry.register(INTERNAL_TRANSFORMER_FAULT)
    registry.register(MAGNETIZING_INRUSH)

    assert registry.all() == (
        INTERNAL_TRANSFORMER_FAULT,
        MAGNETIZING_INRUSH,
    )


def test_registry_queries_by_domain():
    registry = EngineeringKnowledgeRegistry(
        TRANSFORMER_KNOWLEDGE
    )

    results = registry.by_domain("transformer")

    assert results == TRANSFORMER_KNOWLEDGE
    assert registry.by_domain("generator") == ()


def test_registry_queries_by_category():
    registry = EngineeringKnowledgeRegistry(
        TRANSFORMER_KNOWLEDGE
    )

    results = registry.by_category("failure_mode")

    assert results == (
        INTERNAL_TRANSFORMER_FAULT,
    )


def test_registry_queries_by_status():
    registry = EngineeringKnowledgeRegistry(
        TRANSFORMER_KNOWLEDGE
    )

    assert registry.by_status("draft") == (
        TRANSFORMER_KNOWLEDGE
    )
    assert registry.by_status("approved") == ()


def test_registry_accepts_initial_knowledge_collection():
    registry = EngineeringKnowledgeRegistry(
        TRANSFORMER_KNOWLEDGE
    )

    assert registry.all() == TRANSFORMER_KNOWLEDGE


def test_registry_collection_results_are_read_only_tuples():
    registry = EngineeringKnowledgeRegistry(
        TRANSFORMER_KNOWLEDGE
    )

    assert isinstance(registry.all(), tuple)
    assert isinstance(
        registry.by_domain("transformer"),
        tuple,
    )
    assert isinstance(
        registry.by_category("failure_mode"),
        tuple,
    )
    assert isinstance(
        registry.by_status("draft"),
        tuple,
    )


def test_registry_initial_collection_rejects_duplicate_ids():
    with pytest.raises(
        ValueError,
        match="already registered",
    ):
        EngineeringKnowledgeRegistry(
            (
                INTERNAL_TRANSFORMER_FAULT,
                INTERNAL_TRANSFORMER_FAULT,
            )
        )


def test_registry_initial_collection_uses_registration_validation():
    with pytest.raises(
        TypeError,
        match="EngineeringKnowledgeObject",
    ):
        EngineeringKnowledgeRegistry(
            (
                INTERNAL_TRANSFORMER_FAULT,
                {
                    "knowledge_id": "TR-EKO-9999",
                },
            )
        )


def test_duplicate_registration_preserves_existing_object():
    registry = EngineeringKnowledgeRegistry()
    registry.register(INTERNAL_TRANSFORMER_FAULT)

    before = registry.all()

    with pytest.raises(
        ValueError,
        match="already registered",
    ):
        registry.register(INTERNAL_TRANSFORMER_FAULT)

    assert registry.all() == before
    assert registry.get("TR-EKO-0001") is (
        INTERNAL_TRANSFORMER_FAULT
    )


def test_invalid_registration_does_not_mutate_registry():
    registry = EngineeringKnowledgeRegistry(
        (
            INTERNAL_TRANSFORMER_FAULT,
        )
    )

    before = registry.all()

    with pytest.raises(
        TypeError,
        match="EngineeringKnowledgeObject",
    ):
        registry.register(
            {
                "knowledge_id": "TR-EKO-9999",
            }
        )

    assert registry.all() == before


def test_registry_queries_preserve_exact_object_identity():
    registry = EngineeringKnowledgeRegistry(
        TRANSFORMER_KNOWLEDGE
    )

    assert registry.get("TR-EKO-0001") is (
        INTERNAL_TRANSFORMER_FAULT
    )
    assert registry.by_domain("transformer")[0] is (
        INTERNAL_TRANSFORMER_FAULT
    )
    assert registry.by_category("failure_mode")[0] is (
        INTERNAL_TRANSFORMER_FAULT
    )
    assert registry.by_status("draft")[0] is (
        INTERNAL_TRANSFORMER_FAULT
    )


def test_registry_unknown_queries_return_empty_tuples():
    registry = EngineeringKnowledgeRegistry(
        TRANSFORMER_KNOWLEDGE
    )

    assert registry.by_domain("unknown-domain") == ()
    assert registry.by_category("unknown-category") == ()
    assert registry.by_status("unknown-status") == ()
