import pytest

from app.capabilities.contracts import (
    CapabilityRequest,
)
from app.capabilities.evidence_interpretation.capability import (
    EVIDENCE_INTERPRETATION_CAPABILITY_ID,
    EvidenceInterpretationCapability,
)
from app.capabilities.evidence_interpretation.contracts import (
    EvidenceInterpretationRequest,
)
from app.capabilities.evidence_interpretation.runtime import (
    execute_evidence_interpretation,
)


def test_runtime_interprets_known_evidence() -> None:
    result = execute_evidence_interpretation(
        request=EvidenceInterpretationRequest(
            domain="transformer",
            asset_type="power_transformer",
            available_evidence=(
                "DGA report",
                "COMTRADE waveform",
            ),
            investigation_stage="initial",
        ),
    )

    assert len(result.interpretations) == 2
    assert result.unresolved_evidence == ()


def test_runtime_keeps_unknown_evidence_unresolved() -> None:
    result = execute_evidence_interpretation(
        request=EvidenceInterpretationRequest(
            domain="transformer",
            asset_type="power_transformer",
            available_evidence=(
                "Unknown diagnostic flag",
            ),
            investigation_stage="initial",
        ),
    )

    assert result.interpretations == ()
    assert result.unresolved_evidence == (
        "Unknown diagnostic flag",
    )


def test_runtime_does_not_interpret_missing_evidence() -> None:
    result = execute_evidence_interpretation(
        request=EvidenceInterpretationRequest(
            domain="transformer",
            asset_type="power_transformer",
            available_evidence=(),
            missing_evidence=(
                "DGA report",
            ),
            investigation_stage="initial",
        ),
    )

    assert result.interpretations == ()
    assert result.unresolved_evidence == ()


def test_capability_metadata_is_shadow_only() -> None:
    capability = EvidenceInterpretationCapability()

    metadata = capability.metadata()

    assert metadata.capability_id == (
        EVIDENCE_INTERPRETATION_CAPABILITY_ID
    )
    assert metadata.shadow_only is True
    assert metadata.affects_decision is False


def test_capability_rejects_non_shadow_execution() -> None:
    capability = EvidenceInterpretationCapability()

    request = CapabilityRequest(
        request_id="REQ-EVIDENCE-0001",
        payload={
            "domain": "transformer",
            "asset_type": "power_transformer",
            "available_evidence": (
                "DGA report",
            ),
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


def test_capability_returns_interpretation_result() -> None:
    capability = EvidenceInterpretationCapability()

    request = CapabilityRequest(
        request_id="REQ-EVIDENCE-0002",
        payload={
            "domain": "transformer",
            "asset_type": "power_transformer",
            "available_evidence": (
                "Buchholz relay status",
                "DGA report",
            ),
            "investigation_stage": "initial",
        },
        context={
            "execution_mode": "shadow",
        },
    )

    result = capability.execute(request)

    assert result.status == "success"
    assert result.affects_decision is False

    output = result.output[
        "evidence_interpretation_result"
    ]

    assert len(output["interpretations"]) == 2
    assert output["unresolved_evidence"] == ()


def test_capability_audit_reports_counts() -> None:
    capability = EvidenceInterpretationCapability()

    request = CapabilityRequest(
        request_id="REQ-EVIDENCE-0003",
        payload={
            "domain": "transformer",
            "asset_type": "power_transformer",
            "available_evidence": (
                "DGA report",
                "Unknown diagnostic flag",
            ),
            "investigation_stage": "initial",
        },
        context={
            "execution_mode": "shadow",
        },
    )

    result = capability.execute(request)
    audit = capability.audit(result)

    assert audit["interpretation_count"] == 1
    assert audit["unresolved_count"] == 1
    assert audit["shadow_only"] is True
    assert audit["affects_decision"] is False