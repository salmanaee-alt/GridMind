from __future__ import annotations

from typing import Any

from app.capabilities.base import (
    EngineeringCapability,
)
from app.capabilities.contracts import (
    CAPABILITY_ABI_VERSION,
    CapabilityMetadata,
    CapabilityRequest,
    CapabilityResult,
)
from app.capabilities.knowledge_relevance.contracts import (
    KnowledgeRelevanceRequest,
)
from app.capabilities.knowledge_relevance.runtime import (
    execute_knowledge_relevance,
)
from app.knowledge.registry import (
    EngineeringKnowledgeRegistry,
)


KNOWLEDGE_RELEVANCE_CAPABILITY_ID = (
    "CAP-KNOWLEDGERELEVANCE-0001"
)


class KnowledgeRelevanceCapability(
    EngineeringCapability
):
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
                "KnowledgeRelevanceCapability requires an "
                "EngineeringKnowledgeRegistry."
            )

        self._registry = registry

    def metadata(self) -> CapabilityMetadata:
        return CapabilityMetadata(
            capability_id=(
                KNOWLEDGE_RELEVANCE_CAPABILITY_ID
            ),
            name="Knowledge Relevance",
            version="1.0.0",
            abi_version=CAPABILITY_ABI_VERSION,
            shadow_only=True,
            affects_decision=False,
        )

    def validate(
        self,
        request: CapabilityRequest,
    ) -> None:
        if not isinstance(
            request,
            CapabilityRequest,
        ):
            raise TypeError(
                "KnowledgeRelevanceCapability requires a "
                "CapabilityRequest."
            )

        execution_mode = request.context.get(
            "execution_mode"
        )

        if execution_mode != "shadow":
            raise ValueError(
                "Knowledge Relevance Capability supports "
                "shadow execution only."
            )

        KnowledgeRelevanceRequest(
            **request.payload
        )

    def execute(
        self,
        request: CapabilityRequest,
    ) -> CapabilityResult:
        self.validate(request)

        relevance_request = KnowledgeRelevanceRequest(
            **request.payload
        )

        relevance_result = execute_knowledge_relevance(
            registry=self._registry,
            request=relevance_request,
        )

        return CapabilityResult(
            capability_id=(
                KNOWLEDGE_RELEVANCE_CAPABILITY_ID
            ),
            status="success",
            output={
                "knowledge_relevance_result": (
                    relevance_result.model_dump()
                ),
            },
            audit={
                "execution_mode": "shadow",
                "selected_count": len(
                    relevance_result.selected_ids
                ),
                "ignored_count": len(
                    relevance_result.ignored_ids
                ),
                "affects_decision": False,
            },
            affects_decision=False,
        )

    def audit(
        self,
        result: CapabilityResult,
    ) -> dict[str, Any]:
        if result.capability_id != (
            KNOWLEDGE_RELEVANCE_CAPABILITY_ID
        ):
            raise ValueError(
                "Capability result capability_id does not "
                "match Knowledge Relevance Capability."
            )

        relevance_result = result.output.get(
            "knowledge_relevance_result",
            {},
        )

        return {
            "capability_id": (
                KNOWLEDGE_RELEVANCE_CAPABILITY_ID
            ),
            "status": result.status,
            "selected_count": len(
                relevance_result.get(
                    "selected_ids",
                    (),
                )
            ),
            "ignored_count": len(
                relevance_result.get(
                    "ignored_ids",
                    (),
                )
            ),
            "shadow_only": True,
            "affects_decision": False,
        }