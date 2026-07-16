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
from app.capabilities.errors import (
    CapabilityError,
)
from app.capabilities.manifest import (
    CapabilityManifest,
)
from app.capabilities.registry import (
    CapabilityRegistry,
)
from app.capabilities.runtime import (
    CapabilityRuntime,
)


class StageCapability(EngineeringCapability):
    def __init__(
        self,
        *,
        fail_stage: str | None = None,
    ) -> None:
        self.fail_stage = fail_stage

    def metadata(self) -> CapabilityMetadata:
        return CapabilityMetadata(
            capability_id="CAP-TEST-2001",
            name="Stage Capability",
            version="1.0.0",
            abi_version=CAPABILITY_ABI_VERSION,
            shadow_only=True,
            affects_decision=False,
        )

    def validate(
        self,
        request: CapabilityRequest,
    ) -> None:
        if self.fail_stage == "validate":
            raise ValueError("validation failed")

    def execute(
        self,
        request: CapabilityRequest,
    ) -> CapabilityResult:
        if self.fail_stage == "execute":
            raise RuntimeError("execution failed")

        return CapabilityResult(
            capability_id="CAP-TEST-2001",
            status="success",
            output={},
            audit={},
            affects_decision=False,
        )

    def audit(
        self,
        result: CapabilityResult,
    ) -> dict[str, Any]:
        if self.fail_stage == "audit":
            raise RuntimeError("audit failed")

        return {}


class InvalidResultCapability(StageCapability):
    def execute(
        self,
        request: CapabilityRequest,
    ) -> CapabilityResult:
        return CapabilityResult(
            capability_id="CAP-TEST-9999",
            status="success",
            output={},
            audit={},
            affects_decision=False,
        )


def build_manifest() -> CapabilityManifest:
    return CapabilityManifest(
        capability_id="CAP-TEST-2001",
        name="Stage Capability",
        version="1.0.0",
        abi_version=CAPABILITY_ABI_VERSION,
        domain="test",
        requires=(),
        produces=(),
        shadow_only=True,
        affects_decision=False,
        status="experimental",
        author="GridMind AI",
    )


def build_runtime(
    capability: EngineeringCapability,
) -> CapabilityRuntime:
    registry = CapabilityRegistry()
    registry.register(
        capability=capability,
        manifest=build_manifest(),
    )

    return CapabilityRuntime(
        registry=registry,
    )


def build_request() -> CapabilityRequest:
    return CapabilityRequest(
        request_id="REQ-RUNTIME-ERROR-0001",
        payload={},
        context={
            "execution_mode": "shadow",
        },
    )


def test_validation_error_is_classified():
    execution = build_runtime(
        StageCapability(
            fail_stage="validate",
        )
    ).invoke(
        capability_id="CAP-TEST-2001",
        request=build_request(),
    )

    assert isinstance(
        execution.error,
        CapabilityError,
    )
    assert execution.error.error_type == (
        "validation_error"
    )
    assert execution.error.stage == "validate"
    assert execution.error.request_id == (
        "REQ-RUNTIME-ERROR-0001"
    )


def test_execution_error_is_classified():
    execution = build_runtime(
        StageCapability(
            fail_stage="execute",
        )
    ).invoke(
        capability_id="CAP-TEST-2001",
        request=build_request(),
    )

    assert execution.error.error_type == (
        "execution_error"
    )
    assert execution.error.stage == "execute"


def test_audit_error_is_classified():
    execution = build_runtime(
        StageCapability(
            fail_stage="audit",
        )
    ).invoke(
        capability_id="CAP-TEST-2001",
        request=build_request(),
    )

    assert execution.error.error_type == (
        "audit_error"
    )
    assert execution.error.stage == "audit"


def test_result_integrity_error_is_classified():
    registry = CapabilityRegistry()
    capability = InvalidResultCapability()

    registry.register(
        capability=capability,
        manifest=build_manifest(),
    )

    execution = CapabilityRuntime(
        registry=registry,
    ).invoke(
        capability_id="CAP-TEST-2001",
        request=build_request(),
    )

    assert execution.error.error_type == (
        "result_integrity_error"
    )
    assert execution.error.stage == "runtime"


def test_not_found_error_contains_request_context():
    runtime = CapabilityRuntime(
        registry=CapabilityRegistry(),
    )

    execution = runtime.invoke(
        capability_id="CAP-TEST-9999",
        request=build_request(),
    )

    assert execution.error.error_type == "not_found"
    assert execution.error.stage == "runtime"
    assert execution.error.capability_id == (
        "CAP-TEST-9999"
    )
    assert execution.error.request_id == (
        "REQ-RUNTIME-ERROR-0001"
    )


def test_shadow_mode_error_is_structured():
    runtime = build_runtime(
        StageCapability()
    )

    request = CapabilityRequest(
        request_id="REQ-RUNTIME-ERROR-0002",
        payload={},
        context={
            "execution_mode": "active",
        },
    )

    execution = runtime.invoke(
        capability_id="CAP-TEST-2001",
        request=request,
    )

    assert execution.error.error_type == (
        "shadow_mode_required"
    )
    assert execution.error.stage == "runtime"
    assert execution.error.retryable is False
