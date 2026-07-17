from app.capabilities.knowledge_relevance.contracts import (
    KnowledgeRelevanceRequest,
    KnowledgeRelevanceResult,
)
from app.capabilities.knowledge_relevance.projection import (
    project_knowledge_candidate,
)
from app.capabilities.knowledge_relevance.scoring import (
    rank_knowledge_candidates,
)
from app.knowledge.registry import (
    EngineeringKnowledgeRegistry,
)


def execute_knowledge_relevance(
    *,
    registry: EngineeringKnowledgeRegistry,
    request: KnowledgeRelevanceRequest,
) -> KnowledgeRelevanceResult:
    if not isinstance(
        registry,
        EngineeringKnowledgeRegistry,
    ):
        raise TypeError(
            "execute_knowledge_relevance requires an "
            "EngineeringKnowledgeRegistry."
        )

    if not isinstance(
        request,
        KnowledgeRelevanceRequest,
    ):
        raise TypeError(
            "execute_knowledge_relevance requires a "
            "KnowledgeRelevanceRequest."
        )

    candidates = tuple(
        project_knowledge_candidate(knowledge)
        for knowledge in registry.all()
        if knowledge.status != "deprecated"
    )

    return rank_knowledge_candidates(
        request=request,
        candidates=candidates,
    )
