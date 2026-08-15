import pytest
from pydantic import ValidationError

from app.capabilities.contracts import (
    CAPABILITY_ABI_VERSION,
)
from app.capabilities.manifest import (
    CapabilityManifest,
)


def build_manifest() -> CapabilityManifest:
    return CapabilityManifest(
        capability_id="CAP-KNOWLEDGE-0001",
        name="Knowledge Candidate Generator",
        version="1.0.0",
        abi_version=CAPABILITY_ABI_VERSION,
        domain="knowledge",
        requires=(
            "knowledge_context",
        ),
        produces=(
            "knowledge_candidates",
        ),
        shadow_only=True,
        affects_decision=False,
        status="experimental",
        author="GridMind AI",
    )


def test_manifest_accepts_valid_structure():
    manifest = build_manifest()

    assert manifest.capability_id == (
        "CAP-KNOWLEDGE-0001"
    )
    assert manifest.domain == "knowledge"
    assert manifest.requires == (
        "knowledge_context",
    )
    assert manifest.produces == (
        "knowledge_candidates",
    )
    assert manifest.status == "experimental"
    assert manifest.shadow_only is True
    assert manifest.affects_decision is False


def test_manifest_uses_current_abi_version():
    manifest = build_manifest()

    assert manifest.abi_version == (
        CAPABILITY_ABI_VERSION
    )


def test_manifest_models_are_read_only():
    manifest = build_manifest()

    with pytest.raises(ValidationError):
        manifest.version = "2.0.0"

    with pytest.raises(ValidationError):
        manifest.status = "approved"


def test_manifest_forbids_unknown_fields():
    payload = build_manifest().model_dump()
    payload["unexpected"] = True

    with pytest.raises(ValidationError):
        CapabilityManifest(**payload)


@pytest.mark.parametrize(
    "invalid_status",
    [
        "",
        "draft",
        "active",
        "unknown",
    ],
)
def test_manifest_rejects_invalid_status(
    invalid_status: str,
):
    payload = build_manifest().model_dump()
    payload["status"] = invalid_status

    with pytest.raises(ValidationError):
        CapabilityManifest(**payload)


@pytest.mark.parametrize(
    "invalid_domain",
    [
        "",
        "Knowledge",
        "knowledge domain",
        "knowledge/domain",
    ],
)
def test_manifest_rejects_invalid_domain(
    invalid_domain: str,
):
    payload = build_manifest().model_dump()
    payload["domain"] = invalid_domain

    with pytest.raises(ValidationError):
        CapabilityManifest(**payload)


def test_manifest_requires_and_produces_are_tuples():
    manifest = build_manifest()

    assert isinstance(manifest.requires, tuple)
    assert isinstance(manifest.produces, tuple)


def test_manifest_rejects_duplicate_requirements():
    payload = build_manifest().model_dump()
    payload["requires"] = (
        "knowledge_context",
        "knowledge_context",
    )

    with pytest.raises(
        ValidationError,
        match="requires",
    ):
        CapabilityManifest(**payload)


def test_manifest_rejects_duplicate_outputs():
    payload = build_manifest().model_dump()
    payload["produces"] = (
        "knowledge_candidates",
        "knowledge_candidates",
    )

    with pytest.raises(
        ValidationError,
        match="produces",
    ):
        CapabilityManifest(**payload)


def test_manifest_rejects_blank_contract_entries():
    payload = build_manifest().model_dump()
    payload["requires"] = (
        "",
    )

    with pytest.raises(ValidationError):
        CapabilityManifest(**payload)


def test_manifest_rejects_decision_affecting_capability():
    payload = build_manifest().model_dump()
    payload["affects_decision"] = True

    with pytest.raises(ValidationError):
        CapabilityManifest(**payload)


def test_manifest_rejects_incompatible_abi_version():
    payload = build_manifest().model_dump()
    payload["abi_version"] = "2.0"

    with pytest.raises(
        ValidationError,
        match="ABI",
    ):
        CapabilityManifest(**payload)


def test_manifest_preserves_registration_order_contracts():
    manifest = CapabilityManifest(
        capability_id="CAP-TEST-0002",
        name="Ordered Capability",
        version="1.0.0",
        abi_version=CAPABILITY_ABI_VERSION,
        domain="test",
        requires=(
            "first_input",
            "second_input",
        ),
        produces=(
            "first_output",
            "second_output",
        ),
        shadow_only=True,
        affects_decision=False,
        status="experimental",
        author="GridMind AI",
    )

    assert manifest.requires == (
        "first_input",
        "second_input",
    )
    assert manifest.produces == (
        "first_output",
        "second_output",
    )


def test_manifest_rejects_non_shadow_mode():
    payload = build_manifest().model_dump()
    payload["shadow_only"] = False

    with pytest.raises(ValidationError):
        CapabilityManifest(**payload)