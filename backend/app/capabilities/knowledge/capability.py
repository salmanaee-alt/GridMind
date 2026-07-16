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
from app.capabilities.knowledge.generator import (
    KnowledgeCandidateGenerator,
)
from app.knowledge.registry import (
    EngineeringKnowledgeRegistry,
)


KNOWLEDGE_CANDIDATE_CAPABILITY_ID = (
    "CAP-KNOWLEDGE-0001"
)


class KnowledgeCandidateCapability(
    EngineeringCapability
):
    def __init__(
        self,
        *,
        registry: EngineeringKnowledgeRegistry,
    ) -> None:
        self._generator = (
            KnowledgeCandidateGenerator(
                registry=registry,
            )
        )

    def metadata(self) -> CapabilityMetadata:
        return CapabilityMetadata(
            capability_id=(
                KNOWLEDGE_CANDIDATE_CAPABILITY_ID
            ),
            name="Knowledge Candidate Generator",
            version="1.0.0",
            abi_version=CAPABILITY_ABI_VERSION,
            shadow_only=True,
            affects_decision=False,
        )

    def validate(
        self,
        request: CapabilityRequest,
    ) -> None:
        domain = request.payload.get(
            "domain"
        )

        if not isinstance(domain, str):
            raise ValueError(
                "Capability request domain is required."
            )

        execution_mode = request.context.get(
            "execution_mode"
        )

        if execution_mode != "shadow":
            raise ValueError(
                "Knowledge Candidate Capability supports "
                "shadow execution only."
            )


    def execute(
        self,
        request: CapabilityRequest,
    ) -> CapabilityResult:
        self.validate(request)

        domain = request.payload["domain"]

        candidate_result = (
            self._generator.generate(
                domain=domain,
            )
        )

        return CapabilityResult(
            capability_id=(
                KNOWLEDGE_CANDIDATE_CAPABILITY_ID
            ),
            status="success",
            output={
                "knowledge_candidate_result": (
                    candidate_result.model_dump()
                ),
            },
            audit={
                "execution_mode": "shadow",
                "domain": domain,
                "candidate_count": (
                    candidate_result.candidate_count
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
            KNOWLEDGE_CANDIDATE_CAPABILITY_ID
        ):
            raise ValueError(
                "Capability result capability_id does not "
                "match Knowledge Candidate Capability."
            )

        candidate_result = result.output.get(
            "knowledge_candidate_result",
            {},
        )

        return {
            "capability_id": (
                KNOWLEDGE_CANDIDATE_CAPABILITY_ID
            ),
            "status": result.status,
            "candidate_count": (
                candidate_result.get(
                    "candidate_count",
                    0,
                )
            ),
            "shadow_only": True,
            "affects_decision": False,
        }
