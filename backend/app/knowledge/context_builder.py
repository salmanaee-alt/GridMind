from app.knowledge.context import (
    KnowledgeContext,
    KnowledgeReference,
    KnowledgeShadow,
)
from app.knowledge.registry import (
    EngineeringKnowledgeRegistry,
)


KNOWLEDGE_CONTEXT_SCHEMA_VERSION = "1.0.0"


def build_knowledge_context(
    registry: EngineeringKnowledgeRegistry,
    *,
    enabled: bool = True,
) -> KnowledgeContext:
    if not isinstance(
        registry,
        EngineeringKnowledgeRegistry,
    ):
        raise TypeError(
            "build_knowledge_context requires an "
            "EngineeringKnowledgeRegistry."
        )

    knowledge = ()

    if enabled:
        knowledge = tuple(
            KnowledgeReference(
                knowledge_id=item.knowledge_id,
                version=item.version,
                status=item.status,
            )
            for item in registry.all()
        )

    return KnowledgeContext(
        schema_version=KNOWLEDGE_CONTEXT_SCHEMA_VERSION,
        shadow=KnowledgeShadow(
            enabled=enabled,
            source="registry",
            knowledge=knowledge,
            affects_decision=False,
        ),
    )
