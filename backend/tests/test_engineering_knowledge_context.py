import pytest
from pydantic import ValidationError

from app.knowledge.context import (
    KnowledgeContext,
    KnowledgeReference,
    KnowledgeShadow,
)


def build_valid_context() -> KnowledgeContext:
    return KnowledgeContext(
        schema_version="1.0.0",
        shadow=KnowledgeShadow(
            enabled=True,
            source="registry",
            knowledge=(
                KnowledgeReference(
                    knowledge_id="TR-EKO-0001",
                    version="1.0.1",
                    status="draft",
                ),
                KnowledgeReference(
                    knowledge_id="TR-EKO-0002",
                    version="1.0.1",
                    status="draft",
                ),
            ),
            affects_decision=False,
        ),
    )


def test_knowledge_context_accepts_valid_structure():
    context = build_valid_context()

    assert context.schema_version == "1.0.0"
    assert context.shadow.enabled is True
    assert context.shadow.source == "registry"
    assert context.shadow.affects_decision is False
    assert len(context.shadow.knowledge) == 2


def test_knowledge_context_preserves_knowledge_order():
    context = build_valid_context()

    assert [
        item.knowledge_id
        for item in context.shadow.knowledge
    ] == [
        "TR-EKO-0001",
        "TR-EKO-0002",
    ]


def test_knowledge_collection_is_a_tuple():
    context = build_valid_context()

    assert isinstance(
        context.shadow.knowledge,
        tuple,
    )


def test_context_models_forbid_unknown_fields():
    payload = build_valid_context().model_dump()
    payload["unexpected"] = True

    with pytest.raises(ValidationError):
        KnowledgeContext(**payload)

    shadow_payload = build_valid_context().shadow.model_dump()
    shadow_payload["unexpected"] = True

    with pytest.raises(ValidationError):
        KnowledgeShadow(**shadow_payload)


def test_context_models_are_read_only():
    context = build_valid_context()
    reference = context.shadow.knowledge[0]

    with pytest.raises(ValidationError):
        context.schema_version = "2.0.0"

    with pytest.raises(ValidationError):
        context.shadow.enabled = False

    with pytest.raises(ValidationError):
        reference.version = "2.0.0"


def test_affects_decision_accepts_false_only():
    with pytest.raises(ValidationError):
        KnowledgeShadow(
            enabled=True,
            source="registry",
            knowledge=(),
            affects_decision=True,
        )


def test_source_accepts_registry_only():
    with pytest.raises(ValidationError):
        KnowledgeShadow(
            enabled=True,
            source="database",
            knowledge=(),
            affects_decision=False,
        )


@pytest.mark.parametrize(
    "invalid_version",
    [
        "",
        "1",
        "1.0",
        "v1.0.0",
        "1.0.0.0",
    ],
)
def test_context_rejects_invalid_schema_version(
    invalid_version: str,
):
    with pytest.raises(ValidationError):
        KnowledgeContext(
            schema_version=invalid_version,
            shadow=KnowledgeShadow(
                enabled=True,
                source="registry",
                knowledge=(),
                affects_decision=False,
            ),
        )


@pytest.mark.parametrize(
    "invalid_id",
    [
        "",
        "invalid-id",
        "TR-0001",
        "tr-EKO-0001",
    ],
)
def test_reference_rejects_invalid_knowledge_id(
    invalid_id: str,
):
    with pytest.raises(ValidationError):
        KnowledgeReference(
            knowledge_id=invalid_id,
            version="1.0.1",
            status="draft",
        )


@pytest.mark.parametrize(
    "invalid_version",
    [
        "",
        "1",
        "1.0",
        "v1.0.0",
    ],
)
def test_reference_rejects_invalid_version(
    invalid_version: str,
):
    with pytest.raises(ValidationError):
        KnowledgeReference(
            knowledge_id="TR-EKO-0001",
            version=invalid_version,
            status="draft",
        )


def test_reference_rejects_blank_status():
    with pytest.raises(ValidationError):
        KnowledgeReference(
            knowledge_id="TR-EKO-0001",
            version="1.0.1",
            status="   ",
        )


def test_reference_rejects_unknown_status():
    with pytest.raises(ValidationError):
        KnowledgeReference(
            knowledge_id="TR-EKO-0001",
            version="1.0.1",
            status="uncontrolled",
        )
