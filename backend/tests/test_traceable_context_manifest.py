from app.capabilities.contracts import (
    CAPABILITY_ABI_VERSION,
)
from app.capabilities.traceable_context.capability import (
    TRACEABLE_CONTEXT_CAPABILITY_ID,
)
from app.capabilities.traceable_context.capability_manifest import (
    TRACEABLE_CONTEXT_CAPABILITY_MANIFEST,
)


def test_traceable_context_manifest_identity() -> None:
    manifest = TRACEABLE_CONTEXT_CAPABILITY_MANIFEST

    assert manifest.capability_id == (
        TRACEABLE_CONTEXT_CAPABILITY_ID
    )
    assert manifest.name == (
        "Traceable Engineering Context"
    )
    assert manifest.version == "1.0.0"
    assert manifest.abi_version == (
        CAPABILITY_ABI_VERSION
    )


def test_traceable_context_manifest_domain() -> None:
    manifest = TRACEABLE_CONTEXT_CAPABILITY_MANIFEST

    assert manifest.domain == "transformer"


def test_traceable_context_manifest_contract() -> None:
    manifest = TRACEABLE_CONTEXT_CAPABILITY_MANIFEST

    assert manifest.requires == (
        "domain",
        "asset_type",
        "investigation_stage",
        "selected_knowledge_ids",
        "evidence_items",
    )

    assert manifest.produces == (
        "traceable_engineering_context",
    )


def test_traceable_context_manifest_is_safe_shadow() -> None:
    manifest = TRACEABLE_CONTEXT_CAPABILITY_MANIFEST

    assert manifest.shadow_only is True
    assert manifest.affects_decision is False
    assert manifest.status == "experimental"
    