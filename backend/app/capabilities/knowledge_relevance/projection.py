from app.capabilities.knowledge_relevance.scoring import (
    KnowledgeRelevanceCandidate,
)
from app.knowledge.schema import (
    EngineeringKnowledgeObject,
)


def project_knowledge_candidate(
    knowledge: EngineeringKnowledgeObject,
) -> KnowledgeRelevanceCandidate:
    if not isinstance(
        knowledge,
        EngineeringKnowledgeObject,
    ):
        raise TypeError(
            "project_knowledge_candidate requires an "
            "EngineeringKnowledgeObject."
        )

    return KnowledgeRelevanceCandidate(
        knowledge_id=knowledge.knowledge_id,
        domains=(knowledge.domain,),
        asset_types=(),
        evidence_terms=tuple(
            requirement.evidence_name
            for requirement in knowledge.evidence_requirements
        ),
        investigation_stages=(),
    )
