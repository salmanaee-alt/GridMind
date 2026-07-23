from app.capabilities.contracts import (
    CAPABILITY_ABI_VERSION,
)
from app.capabilities.evidence_interpretation.capability import (
    EVIDENCE_INTERPRETATION_CAPABILITY_ID,
)
from app.capabilities.evidence_interpretation.capability_manifest import (
    EVIDENCE_INTERPRETATION_CAPABILITY_MANIFEST,
)


def test_evidence_interpretation_manifest_identity() -> None:
    manifest = (
        EVIDENCE_INTERPRETATION_CAPABILITY_MANIFEST
    )

    assert manifest.capability_id == (
        EVIDENCE_INTERPRETATION_CAPABILITY_ID
    )
    assert manifest.name == "Evidence Interpretation"
    assert manifest.version == "1.0.0"
    assert manifest.abi_version == CAPABILITY_ABI_VERSION


def test_evidence_interpretation_manifest_domain() -> None:
    manifest = (
        EVIDENCE_INTERPRETATION_CAPABILITY_MANIFEST
    )

    assert manifest.domain == "transformer"


def test_evidence_interpretation_manifest_contract() -> None:
    manifest = (
        EVIDENCE_INTERPRETATION_CAPABILITY_MANIFEST
    )

    assert manifest.requires == (
        "domain",
        "asset_type",
        "available_evidence",
        "investigation_stage",
    )

    assert manifest.produces == (
        "evidence_interpretation_result",
    )


def test_evidence_interpretation_manifest_is_safe_shadow() -> None:
    manifest = (
        EVIDENCE_INTERPRETATION_CAPABILITY_MANIFEST
    )

    assert manifest.shadow_only is True
    assert manifest.affects_decision is False
    assert manifest.status == "experimental"
    