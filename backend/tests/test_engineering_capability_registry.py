from typing import Any

import pytest

from app.capabilities.base import (
    EngineeringCapability,
)
from app.capabilities.contracts import (
    CAPABILITY_ABI_VERSION,
    CapabilityMetadata,
    CapabilityRequest,
    CapabilityResult,
)
from app.capabilities.manifest import (
    CapabilityManifest,
)
from app.capabilities.registry import (
    CapabilityRegistry,
)


class ExampleCapability(EngineeringCapability):
    def metadata(self) -> CapabilityMetadata:
        return CapabilityMetadata(
            capability_id="CAP-TEST-0001",
            name="Example Capability",
            version="1.0.0",
            abi_version=CAPABILITY_ABI_VERSION,
            shadow_only=True,
            affects_decision=False,
        )

    def validate(
        self,
        request: CapabilityRequest,
    ) -> None:
        return None

    def execute(
        self,
        request: CapabilityRequest,
    ) -> CapabilityResult:
        return CapabilityResult(
            capability_id=self.metadata().capability_id,
            status="success",
            output={},
            audit={},
            affects_decision=False,
        )

    def audit(
        self,
        result: CapabilityResult,
    ) -> dict[str, Any]:
        return {
            "capability_id": result.capability_id,
        }


class SecondCapability(EngineeringCapability):
    def metadata(self) -> CapabilityMetadata:
        return CapabilityMetadata(
            capability_id="CAP-TEST-0002",
            name="Second Capability",
            version="1.0.0",
            abi_version=CAPABILITY_ABI_VERSION,
            shadow_only=True,
            affects_decision=False,
        )

    def validate(
        self,
        request: CapabilityRequest,
    ) -> None:
        return None

    def execute(
        self,
        request: CapabilityRequest,
    ) -> CapabilityResult:
        return CapabilityResult(
            capability_id=self.metadata().capability_id,
            status="success",
            output={},
            audit={},
            affects_decision=False,
        )

    def audit(
        self,
        result: CapabilityResult,
    ) -> dict[str, Any]:
        return {
            "capability_id": result.capability_id,
        }


def build_manifest(
    *,
    capability_id: str = "CAP-TEST-0001",
    name: str = "Example Capability",
    version: str = "1.0.0",
    abi_version: str = CAPABILITY_ABI_VERSION,
) -> CapabilityManifest:
    return CapabilityManifest(
        capability_id=capability_id,
        name=name,
        version=version,
        abi_version=abi_version,
        domain="test",
        requires=(),
        produces=(),
        shadow_only=True,
        affects_decision=False,
        status="experimental",
        author="GridMind AI",
    )


def test_registry_starts_empty():
    registry = CapabilityRegistry()

    assert registry.all() == ()
    assert registry.exists("CAP-TEST-0001") is False
    assert registry.get("CAP-TEST-0001") is None


def test_registry_registers_capability_and_manifest():
    registry = CapabilityRegistry()
    capability = ExampleCapability()
    manifest = build_manifest()

    registry.register(
        capability=capability,
        manifest=manifest,
    )

    registration = registry.get("CAP-TEST-0001")

    assert registration is not None
    assert registration.capability is capability
    assert registration.manifest is manifest
    assert registry.exists("CAP-TEST-0001") is True


def test_registry_preserves_registration_order():
    registry = CapabilityRegistry()

    first = ExampleCapability()
    second = SecondCapability()

    registry.register(
        capability=first,
        manifest=build_manifest(),
    )
    registry.register(
        capability=second,
        manifest=build_manifest(
            capability_id="CAP-TEST-0002",
            name="Second Capability",
        ),
    )

    registrations = registry.all()

    assert tuple(
        item.manifest.capability_id
        for item in registrations
    ) == (
        "CAP-TEST-0001",
        "CAP-TEST-0002",
    )


def test_registry_rejects_duplicate_capability_id():
    registry = CapabilityRegistry()

    registry.register(
        capability=ExampleCapability(),
        manifest=build_manifest(),
    )

    with pytest.raises(
        ValueError,
        match="already registered",
    ):
        registry.register(
            capability=ExampleCapability(),
            manifest=build_manifest(),
        )


def test_duplicate_failure_preserves_existing_registration():
    registry = CapabilityRegistry()
    original = ExampleCapability()
    manifest = build_manifest()

    registry.register(
        capability=original,
        manifest=manifest,
    )

    before = registry.all()

    with pytest.raises(ValueError):
        registry.register(
            capability=ExampleCapability(),
            manifest=build_manifest(),
        )

    assert registry.all() == before
    assert registry.get(
        "CAP-TEST-0001"
    ).capability is original


def test_registry_rejects_non_capability_object():
    registry = CapabilityRegistry()

    with pytest.raises(
        TypeError,
        match="EngineeringCapability",
    ):
        registry.register(
            capability=object(),
            manifest=build_manifest(),
        )


def test_registry_rejects_non_manifest_object():
    registry = CapabilityRegistry()

    with pytest.raises(
        TypeError,
        match="CapabilityManifest",
    ):
        registry.register(
            capability=ExampleCapability(),
            manifest={},
        )


def test_registry_rejects_metadata_manifest_id_mismatch():
    registry = CapabilityRegistry()

    with pytest.raises(
        ValueError,
        match="capability_id",
    ):
        registry.register(
            capability=ExampleCapability(),
            manifest=build_manifest(
                capability_id="CAP-TEST-9999",
            ),
        )


def test_registry_rejects_metadata_manifest_name_mismatch():
    registry = CapabilityRegistry()

    with pytest.raises(
        ValueError,
        match="name",
    ):
        registry.register(
            capability=ExampleCapability(),
            manifest=build_manifest(
                name="Different Capability",
            ),
        )


def test_registry_rejects_metadata_manifest_version_mismatch():
    registry = CapabilityRegistry()

    with pytest.raises(
        ValueError,
        match="version",
    ):
        registry.register(
            capability=ExampleCapability(),
            manifest=build_manifest(
                version="1.0.1",
            ),
        )


def test_registry_rejects_incompatible_metadata_abi():
    class IncompatibleCapability(ExampleCapability):
        def metadata(self) -> CapabilityMetadata:
            return CapabilityMetadata(
                capability_id="CAP-TEST-0001",
                name="Example Capability",
                version="1.0.0",
                abi_version="2.0",
                shadow_only=True,
                affects_decision=False,
            )

    registry = CapabilityRegistry()

    with pytest.raises(
        ValueError,
        match="ABI",
    ):
        registry.register(
            capability=IncompatibleCapability(),
            manifest=build_manifest(),
        )


def test_registry_results_are_read_only_tuples():
    registry = CapabilityRegistry()

    registry.register(
        capability=ExampleCapability(),
        manifest=build_manifest(),
    )

    assert isinstance(registry.all(), tuple)


def test_registry_does_not_execute_capability_on_registration():
    class ExecutionTrackingCapability(ExampleCapability):
        executed = False

        def execute(
            self,
            request: CapabilityRequest,
        ) -> CapabilityResult:
            self.executed = True
            return super().execute(request)

    capability = ExecutionTrackingCapability()
    registry = CapabilityRegistry()

    registry.register(
        capability=capability,
        manifest=build_manifest(),
    )

    assert capability.executed is False
