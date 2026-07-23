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
from app.capabilities.evidence_interpretation.contracts import (
    EvidenceInterpretationRequest,
)
from app.capabilities.evidence_interpretation.runtime import (
    execute_evidence_interpretation,
)


EVIDENCE_INTERPRETATION_CAPABILITY_ID = (
    "CAP-EVIDENCEINTERP-0001"
)


class EvidenceInterpretationCapability(
    EngineeringCapability
):
    def metadata(self) -> CapabilityMetadata:
        return CapabilityMetadata(
            capability_id=(
                EVIDENCE_INTERPRETATION_CAPABILITY_ID
            ),
            name="Evidence Interpretation",
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
                "EvidenceInterpretationCapability requires "
                "a CapabilityRequest."
            )

        execution_mode = request.context.get(
            "execution_mode"
        )

        if execution_mode != "shadow":
            raise ValueError(
                "Evidence Interpretation Capability "
                "supports shadow execution only."
            )

        EvidenceInterpretationRequest(
            **request.payload
        )

    def execute(
        self,
        request: CapabilityRequest,
    ) -> CapabilityResult:
        self.validate(request)

        interpretation_request = (
            EvidenceInterpretationRequest(
                **request.payload
            )
        )

        interpretation_result = (
            execute_evidence_interpretation(
                request=interpretation_request,
            )
        )

        return CapabilityResult(
            capability_id=(
                EVIDENCE_INTERPRETATION_CAPABILITY_ID
            ),
            status="success",
            output={
                "evidence_interpretation_result": (
                    interpretation_result.model_dump()
                ),
            },
            audit={
                "execution_mode": "shadow",
                "interpretation_count": len(
                    interpretation_result.interpretations
                ),
                "unresolved_count": len(
                    interpretation_result.unresolved_evidence
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
            EVIDENCE_INTERPRETATION_CAPABILITY_ID
        ):
            raise ValueError(
                "Capability result capability_id does not "
                "match Evidence Interpretation Capability."
            )

        interpretation_result = result.output.get(
            "evidence_interpretation_result",
            {},
        )

        return {
            "capability_id": (
                EVIDENCE_INTERPRETATION_CAPABILITY_ID
            ),
            "status": result.status,
            "interpretation_count": len(
                interpretation_result.get(
                    "interpretations",
                    (),
                )
            ),
            "unresolved_count": len(
                interpretation_result.get(
                    "unresolved_evidence",
                    (),
                )
            ),
            "shadow_only": True,
            "affects_decision": False,
        }
    