from time import sleep
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
from app.capabilities.manifest import (
    CapabilityManifest,
)
from app.capabilities.registry import (
    CapabilityRegistry,
)
from app.capabilities.runtime import (
    CapabilityRuntime,
)


class FastCapability(EngineeringCapability):
    def metadata(self) -> CapabilityMetadata:
        return CapabilityMetadata(
            capability_id="CAP-TEST-3001",
            name="Fast Capability",
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
            capability_id="CAP-TEST-3001",
            status="success",
            output={
                "value": 1,
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
        }


class SlowCapability(FastCapability):
    def metadata(self) -> CapabilityMetadata:
        return CapabilityMetadata(
            capability_id="CAP-TEST-3002",
            name="Slow Capability",
            version="1.0.0",
            abi_version=CAPABILITY_ABI_VERSION,
            shadow_only=True,
            affects_decision=False,
        )

    def execute(
        self,
        request: CapabilityRequest,
    ) -> CapabilityResult:
        sleep(2)

        return CapabilityResult(
            capability_id="CAP-TEST-3002",
            status="success",
            output={},
            audit={},
            affects_decision=False,
        )


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


def build_runtime(
    *,
    timeout_seconds: float,
) -> CapabilityRuntime:
    registry = CapabilityRegistry()

    registry.register(
        capability=FastCapability(),
        manifest=build_manifest(
            capability_id="CAP-TEST-3001",
            name="Fast Capability",
        ),
    )

    registry.register(
        capability=SlowCapability(),
        manifest=build_manifest(
            capability_id="CAP-TEST-3002",
            name="Slow Capability",
        ),
    )

    return CapabilityRuntime(
        registry=registry,
        timeout_seconds=timeout_seconds,
        process_isolation=True,
    )


def build_request() -> CapabilityRequest:
    return CapabilityRequest(
        request_id="REQ-RUNTIME-ISOLATION-0001",
        payload={},
        context={
            "execution_mode": "shadow",
        },
    )


def test_fast_capability_succeeds_in_isolated_process():
    runtime = build_runtime(
        timeout_seconds=1.0,
    )

    execution = runtime.invoke(
        capability_id="CAP-TEST-3001",
        request=build_request(),
    )

    assert execution.result.status == "success"
    assert execution.result.output == {
        "value": 1,
    }
    assert execution.error is None


def test_slow_capability_is_terminated_on_timeout():
    runtime = build_runtime(
        timeout_seconds=0.2,
    )

    execution = runtime.invoke(
        capability_id="CAP-TEST-3002",
        request=build_request(),
    )

    assert execution.result.status == "error"
    assert execution.error.error_type == "timeout_error"
    assert execution.error.stage == "execute"
    assert execution.error.retryable is True


def test_runtime_recovers_after_timeout():
    runtime = build_runtime(
        timeout_seconds=0.2,
    )

    timed_out = runtime.invoke(
        capability_id="CAP-TEST-3002",
        request=build_request(),
    )

    successful = runtime.invoke(
        capability_id="CAP-TEST-3001",
        request=build_request(),
    )

    assert timed_out.error.error_type == "timeout_error"
    assert successful.result.status == "success"
    assert successful.error is None


def test_timeout_duration_is_bounded():
    runtime = build_runtime(
        timeout_seconds=0.2,
    )

    execution = runtime.invoke(
        capability_id="CAP-TEST-3002",
        request=build_request(),
    )

    assert execution.duration_ms < 1500
