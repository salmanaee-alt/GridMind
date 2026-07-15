from __future__ import annotations

import re

from app.capabilities.knowledge.contracts import (
    CandidateReason,
    CandidateSource,
    KnowledgeCandidate,
    KnowledgeCandidateResult,
)
from app.knowledge.registry import (
    EngineeringKnowledgeRegistry,
)


DOMAIN_PATTERN = re.compile(
    r"^[a-z][a-z0-9_]{1,63}$"
)


class KnowledgeCandidateGenerator:
    def __init__(
        self,
        *,
        registry: EngineeringKnowledgeRegistry,
    ) -> None:
        if not isinstance(
            registry,
            EngineeringKnowledgeRegistry,
        ):
            raise TypeError(
                "KnowledgeCandidateGenerator requires an "
                "EngineeringKnowledgeRegistry."
            )

        self.registry = registry

    def generate(
        self,
        *,
        domain: str,
    ) -> KnowledgeCandidateResult:
        if not isinstance(domain, str):
            raise TypeError(
                "domain must be a string."
            )

        if not DOMAIN_PATTERN.fullmatch(domain):
            raise ValueError(
                "domain must use lowercase letters, numbers, "
                "and underscores only."
            )

        knowledge_objects = self.registry.by_domain(
            domain
        )

        candidates = tuple(
            KnowledgeCandidate(
                knowledge_id=item.knowledge_id,
                source=CandidateSource.REGISTRY,
                reason=CandidateReason(
                    code="domain_match",
                    description=(
                        "Knowledge object matches the "
                        f"{domain} domain."
                    ),
                ),
                shadow_only=True,
                affects_decision=False,
            )
            for item in knowledge_objects
        )

        return KnowledgeCandidateResult(
            candidates=candidates,
            candidate_count=len(candidates),
            shadow_only=True,
            affects_decision=False,
        )
