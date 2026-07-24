import pytest

from app.capabilities.contracts import (
    CapabilityRequest,
)
from app.capabilities.traceable_context.capability import (
    TRACEABLE_CONTEXT_CAPABILITY_ID,
    TraceableContextCapability,
)


def test_traceable_context_capability_metadata() -> None:
    capability = TraceableContextCapability()

    metadata = capability.metadata()

    assert metadata.capability_id == (
        TRACEABLE_CONTEXT_CAPABILITY_ID
    )
    assert metadata.shadow_only is True
    assert metadata.affects_decision is False


def test_traceable_context_capability_rejects_active_mode() -> None:
    capability = TraceableContextCapability()

    request = CapabilityRequest(
        request_id="REQ-TRACEABLE-0001",
        payload={
            "domain": "transformer",
            "asset_type": "power_transformer",
            "investigation_stage": "initial",
        },
        context={
            "execution_mode": "active",
        },
    )

    with pytest.raises(
        ValueError,
        match="shadow execution only",
    ):
        capability.execute(request)


def test_traceable_context_capability_executes() -> None:
    capability = TraceableContextCapability()

    request = CapabilityRequest(
        request_id="REQ-TRACEABLE-0002",
        payload={
            "domain": "transformer",
            "asset_type": "power_transformer",
            "investigation_stage": "initial",
            "selected_knowledge_ids": (
                "EKO-0001",
            ),
            "evidence_items": (
                {
                    "evidence": "DGA report",
                    "interpretation": (
                        "DGA interpretation"
                    ),
                    "engineering_significance": (
                        "Transformer condition evidence."
                    ),
                    "supporting_knowledge_ids": (
                        "EKO-0001",
                    ),
                },
            ),
            "unresolved_evidence": (),
        },
        context={
            "execution_mode": "shadow",
        },
    )

    result = capability.execute(request)

    assert result.status == "success"
    assert result.affects_decision is False

    output = result.output[
        "traceable_engineering_context"
    ]

    assert output["knowledge_ids"] == (
        "EKO-0001",
    )
    assert output["traceability_complete"] is True


def test_traceable_context_capability_audit() -> None:
    capability = TraceableContextCapability()

    request = CapabilityRequest(
        request_id="REQ-TRACEABLE-0003",
        payload={
            "domain": "transformer",
            "asset_type": "power_transformer",
            "investigation_stage": "initial",
            "selected_knowledge_ids": (
                "EKO-0001",
            ),
            "evidence_items": (
                {
                    "evidence": "DGA report",
                    "interpretation": (
                        "DGA interpretation"
                    ),
                    "engineering_significance": (
                        "Transformer condition evidence."
                    ),
                    "supporting_knowledge_ids": (),
                },
            ),
            "unresolved_evidence": (
                "Unknown diagnostic flag",
            ),
        },
        context={
            "execution_mode": "shadow",
        },
    )

    result = capability.execute(request)
    audit = capability.audit(result)

    assert audit["knowledge_count"] == 1
    assert audit["evidence_count"] == 1
    assert audit["unresolved_count"] == 1
    assert audit["traceability_complete"] is False
    assert audit["shadow_only"] is True
    assert audit["affects_decision"] is False
    