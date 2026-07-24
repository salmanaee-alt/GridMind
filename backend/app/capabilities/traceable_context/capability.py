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
from app.capabilities.traceable_context.contracts import (
    TraceableEngineeringContextRequest,
)
from app.capabilities.traceable_context.runtime import (
    execute_traceable_context,
)


TRACEABLE_CONTEXT_CAPABILITY_ID = (
    "CAP-TRACEABLECTX-0001"
)


class TraceableContextCapability(
    EngineeringCapability
):
    def metadata(self) -> CapabilityMetadata:
        return CapabilityMetadata(
            capability_id=(
                TRACEABLE_CONTEXT_CAPABILITY_ID
            ),
            name="Traceable Engineering Context",
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
                "TraceableContextCapability requires "
                "a CapabilityRequest."
            )

        execution_mode = request.context.get(
            "execution_mode"
        )

        if execution_mode != "shadow":
            raise ValueError(
                "Traceable Context Capability supports "
                "shadow execution only."
            )

        TraceableEngineeringContextRequest(
            **request.payload
        )

    def execute(
        self,
        request: CapabilityRequest,
    ) -> CapabilityResult:
        self.validate(request)

        traceable_request = (
            TraceableEngineeringContextRequest(
                **request.payload
            )
        )

        traceable_result = execute_traceable_context(
            request=traceable_request,
        )

        return CapabilityResult(
            capability_id=(
                TRACEABLE_CONTEXT_CAPABILITY_ID
            ),
            status="success",
            output={
                "traceable_engineering_context": (
                    traceable_result.model_dump()
                ),
            },
            audit={
                "execution_mode": "shadow",
                "knowledge_count": len(
                    traceable_result.knowledge_ids
                ),
                "evidence_count": len(
                    traceable_result.evidence_items
                ),
                "unresolved_count": len(
                    traceable_result.unresolved_evidence
                ),
                "traceability_complete": (
                    traceable_result.traceability_complete
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
            TRACEABLE_CONTEXT_CAPABILITY_ID
        ):
            raise ValueError(
                "Capability result capability_id does not "
                "match Traceable Context Capability."
            )

        context_result = result.output.get(
            "traceable_engineering_context",
            {},
        )

        return {
            "capability_id": (
                TRACEABLE_CONTEXT_CAPABILITY_ID
            ),
            "status": result.status,
            "knowledge_count": len(
                context_result.get(
                    "knowledge_ids",
                    (),
                )
            ),
            "evidence_count": len(
                context_result.get(
                    "evidence_items",
                    (),
                )
            ),
            "unresolved_count": len(
                context_result.get(
                    "unresolved_evidence",
                    (),
                )
            ),
            "traceability_complete": (
                context_result.get(
                    "traceability_complete",
                    False,
                )
            ),
            "shadow_only": True,
            "affects_decision": False,
        }
    