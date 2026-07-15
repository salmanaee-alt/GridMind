from app.capabilities.contracts import (
    CAPABILITY_ABI_VERSION,
    CapabilityRequest,
)
from app.capabilities.knowledge.capability import (
    KNOWLEDGE_CANDIDATE_CAPABILITY_ID,
    KnowledgeCandidateCapability,
)
from app.capabilities.knowledge.manifest import (
    KNOWLEDGE_CANDIDATE_MANIFEST,
)
from app.capabilities.registry import (
    CapabilityRegistry,
)
from app.knowledge.bootstrap import (
    build_default_registry,
)


def build_capability() -> KnowledgeCandidateCapability:
    return KnowledgeCandidateCapability(
        registry=build_default_registry(),
    )


def build_request() -> CapabilityRequest:
    return CapabilityRequest(
        request_id="REQ-KNOWLEDGE-INTEGRATION-0001",
        payload={
            "domain": "transformer",
        },
        context={
            "execution_mode": "shadow",
        },
    )


def test_capability_manifest_matches_metadata():
    capability = build_capability()
    metadata = capability.metadata()
    manifest = KNOWLEDGE_CANDIDATE_MANIFEST

    assert manifest.capability_id == metadata.capability_id
    assert manifest.name == metadata.name
    assert manifest.version == metadata.version
    assert manifest.abi_version == metadata.abi_version
    assert manifest.shadow_only == metadata.shadow_only
    assert manifest.affects_decision == (
        metadata.affects_decision
    )


def test_capability_manifest_uses_current_abi():
    assert KNOWLEDGE_CANDIDATE_MANIFEST.abi_version == (
        CAPABILITY_ABI_VERSION
    )


def test_capability_manifest_declares_expected_contracts():
    manifest = KNOWLEDGE_CANDIDATE_MANIFEST

    assert manifest.domain == "knowledge"
    assert manifest.requires == (
        "engineering_knowledge_registry",
        "domain",
    )
    assert manifest.produces == (
        "knowledge_candidate_result",
    )
    assert manifest.status == "experimental"
    assert manifest.shadow_only is True
    assert manifest.affects_decision is False


def test_registry_accepts_capability_001():
    registry = CapabilityRegistry()
    capability = build_capability()

    registry.register(
        capability=capability,
        manifest=KNOWLEDGE_CANDIDATE_MANIFEST,
    )

    registration = registry.get(
        KNOWLEDGE_CANDIDATE_CAPABILITY_ID
    )

    assert registration is not None
    assert registration.capability is capability
    assert registration.manifest is (
        KNOWLEDGE_CANDIDATE_MANIFEST
    )


def test_registry_registration_does_not_execute_capability():
    class TrackingCapability(
        KnowledgeCandidateCapability
    ):
        executed = False

        def execute(self, request):
            self.executed = True
            return super().execute(request)

    capability = TrackingCapability(
        registry=build_default_registry(),
    )
    registry = CapabilityRegistry()

    registry.register(
        capability=capability,
        manifest=KNOWLEDGE_CANDIDATE_MANIFEST,
    )

    assert capability.executed is False


def test_registered_capability_can_execute_manually():
    registry = CapabilityRegistry()
    capability = build_capability()

    registry.register(
        capability=capability,
        manifest=KNOWLEDGE_CANDIDATE_MANIFEST,
    )

    registration = registry.get(
        KNOWLEDGE_CANDIDATE_CAPABILITY_ID
    )

    result = registration.capability.execute(
        build_request()
    )

    assert result.status == "success"
    assert result.affects_decision is False

    candidate_result = result.output[
        "knowledge_candidate_result"
    ]

    assert candidate_result["candidate_count"] == 3


def test_registered_capability_audit_is_shadow_only():
    registry = CapabilityRegistry()
    capability = build_capability()

    registry.register(
        capability=capability,
        manifest=KNOWLEDGE_CANDIDATE_MANIFEST,
    )

    registration = registry.get(
        KNOWLEDGE_CANDIDATE_CAPABILITY_ID
    )

    result = registration.capability.execute(
        build_request()
    )
    audit = registration.capability.audit(
        result
    )

    assert audit["shadow_only"] is True
    assert audit["affects_decision"] is False
    assert result.affects_decision is False


def test_capability_001_has_no_core_dependencies():
    import app.capabilities.knowledge.capability as module

    source_names = set(module.__dict__)

    assert "EngineeringBrain" not in source_names
    assert "EngineeringSession" not in source_names
    assert "InvestigationStatus" not in source_names
