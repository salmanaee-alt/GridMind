from app.knowledge.registry import (
    EngineeringKnowledgeRegistry,
)
from app.knowledge.transformer import (
    TRANSFORMER_KNOWLEDGE,
)


def build_default_registry(
) -> EngineeringKnowledgeRegistry:
    return EngineeringKnowledgeRegistry(
        TRANSFORMER_KNOWLEDGE
    )
