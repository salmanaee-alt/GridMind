from dataclasses import dataclass


@dataclass(frozen=True)
class KnowledgeRelevanceManifest:
    capability_id: str
    name: str
    version: str
    status: str
    shadow_only: bool
    affects_decision: bool
    request_model: str
    result_model: str
    description: str
    capabilities: tuple[str, ...]


KNOWLEDGE_RELEVANCE_MANIFEST = KnowledgeRelevanceManifest(
    capability_id="knowledge_relevance",
    name="Knowledge Relevance Engine",
    version="2.0.0",
    status="experimental",
    shadow_only=True,
    affects_decision=False,
    request_model="KnowledgeRelevanceRequest",
    result_model="KnowledgeRelevanceResult",
    description=(
        "Rank engineering knowledge references by relevance "
        "to the current investigation context."
    ),
    capabilities=(
        "knowledge_relevance_ranking",
        "reference_selection",
        "shadow_analysis",
    ),
)
