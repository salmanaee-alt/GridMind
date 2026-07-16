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
from app.capabilities.runtime import (
    CapabilityRuntime,
)


class SuccessfulCapability(EngineeringCapability):
    def metadata(self) -> CapabilityMetadata:
        return CapabilityMetadata(
            capability_id="CAP-TEST-1001",
            name="Successful Capability",
            version="1.0.0",
            abi_version=CAPABILITY_ABI_VERSION,
            shadow_only=True,
            affects_decision=False,
        )

    def validate(
        self,
        request: CapabilityRequest,
    ) -> None:
        if request.context.get("execution_mode") != "shadow":
            raise ValueError("shadow mode is required")

    def execute(
        self,
        request: CapabilityRequest,
    ) -> CapabilityResult:
        return CapabilityResult(
            capability_id="CAP-TEST-1001",
            status="success",
            output={
                "value": request.payload.get("value"),
            },
            audit={},
            affects_decision=False,
        )

    def audit(
        self,
        result: CapabilityResult,
    ) -> dict[str, Any]:
        return {
            "status": result.status,
            "value": result.output.get("value"),
        }


class FailingCapability(SuccessfulCapability):
    def metadata(self) -> CapabilityMetadata:
        return CapabilityMetadata(
            capability_id="CAP-TEST-1002",
            name="Failing Capability",
            version="1.0.0",
            abi_version=CAPABILITY_ABI_VERSION,
            shadow_only=True,
            affects_decision=False,
        )

    def execute(
        self,
        request: CapabilityRequest,
    ) -> CapabilityResult:
        raise RuntimeError("simulated failure")


def build_manifest(
    *,
    capability_id: str,
    name: str,
) -> CapabilityManifest:
    return CapabilityManifest(
        capability_id=capability_id,
        name=name,
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


def build_runtime() -> CapabilityRuntime:
    registry = CapabilityRegistry()

    registry.register(
        capability=SuccessfulCapability(),
        manifest=build_manifest(
            capability_id="CAP-TEST-1001",
            name="Successful Capability",
        ),
    )

    registry.register(
        capability=FailingCapability(),
        manifest=build_manifest(
            capability_id="CAP-TEST-1002",
            name="Failing Capability",
        ),
    )

    return CapabilityRuntime(
        registry=registry,
    )


def build_request(
    *,
    mode: str = "shadow",
) -> CapabilityRequest:
    return CapabilityRequest(
        request_id="REQ-RUNTIME-0001",
        payload={
            "value": 10,
        },
        context={
            "execution_mode": mode,
        },
    )


def test_runtime_executes_registered_capability():
    runtime = build_runtime()

    execution = runtime.invoke(
        capability_id="CAP-TEST-1001",
        request=build_request(),
    )

    assert execution.result.status == "success"
    assert execution.result.output == {
        "value": 10,
    }
    assert execution.audit == {
        "status": "success",
        "value": 10,
    }
    assert execution.duration_ms >= 0
    assert execution.error is None


def test_runtime_rejects_unknown_capability():
    runtime = build_runtime()

    execution = runtime.invoke(
        capability_id="CAP-TEST-9999",
        request=build_request(),
    )

    assert execution.result.status == "error"
    assert execution.error["type"] == "not_found"
    assert execution.audit == {}
    assert execution.result.affects_decision is False


def test_runtime_enforces_shadow_mode_centrally():
    runtime = build_runtime()

    execution = runtime.invoke(
        capability_id="CAP-TEST-1001",
        request=build_request(
            mode="active",
        ),
    )

    assert execution.result.status == "error"
    assert execution.error["type"] == "shadow_mode_required"


def test_runtime_isolates_execution_exception():
    runtime = build_runtime()

    execution = runtime.invoke(
        capability_id="CAP-TEST-1002",
        request=build_request(),
    )

    assert execution.result.status == "error"
    assert execution.error["type"] == "execution_error"
    assert "simulated failure" in execution.error["message"]
    assert execution.result.affects_decision is False


def test_runtime_preserves_request():
    runtime = build_runtime()
    request = build_request()
    before = request.model_dump()

    runtime.invoke(
        capability_id="CAP-TEST-1001",
        request=request,
    )

    assert request.model_dump() == before


def test_runtime_runs_validate_execute_audit_in_order():
    events: list[str] = []

    class OrderedCapability(SuccessfulCapability):
        def metadata(self) -> CapabilityMetadata:
            return CapabilityMetadata(
                capability_id="CAP-TEST-1003",
                name="Ordered Capability",
                version="1.0.0",
                abi_version=CAPABILITY_ABI_VERSION,
                shadow_only=True,
                affects_decision=False,
            )

        def validate(
            self,
            request: CapabilityRequest,
        ) -> None:
            events.append("validate")

        def execute(
            self,
            request: CapabilityRequest,
        ) -> CapabilityResult:
            events.append("execute")
            return CapabilityResult(
                capability_id="CAP-TEST-1003",
                status="success",
                output={},
                audit={},
                affects_decision=False,
            )

        def audit(
            self,
            result: CapabilityResult,
        ) -> dict[str, Any]:
            events.append("audit")
            return {}

    registry = CapabilityRegistry()
    registry.register(
        capability=OrderedCapability(),
        manifest=build_manifest(
            capability_id="CAP-TEST-1003",
            name="Ordered Capability",
        ),
    )

    runtime = CapabilityRuntime(
        registry=registry,
    )

    runtime.invoke(
        capability_id="CAP-TEST-1003",
        request=build_request(),
    )

    assert events == [
        "validate",
        "execute",
        "audit",
    ]
