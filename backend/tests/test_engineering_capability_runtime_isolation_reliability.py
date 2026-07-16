import multiprocessing
import os
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


class ReliabilityCapability(EngineeringCapability):
    def __init__(
        self,
        *,
        behavior: str = "success",
    ) -> None:
        self.behavior = behavior

    def metadata(self) -> CapabilityMetadata:
        return CapabilityMetadata(
            capability_id="CAP-TEST-4001",
            name="Reliability Capability",
            version="1.0.0",
            abi_version=CAPABILITY_ABI_VERSION,
            shadow_only=True,
            affects_decision=False,
        )

    def validate(
        self,
        request: CapabilityRequest,
    ) -> None:
        if self.behavior == "validation_error":
            raise ValueError(
                "isolated validation failed"
            )

    def execute(
        self,
        request: CapabilityRequest,
    ) -> CapabilityResult:
        if self.behavior == "execution_error":
            raise RuntimeError(
                "isolated execution failed"
            )

        if self.behavior == "crash":
            os._exit(17)

        capability_id = "CAP-TEST-4001"

        if self.behavior == "wrong_id":
            capability_id = "CAP-TEST-4999"

        return CapabilityResult(
            capability_id=capability_id,
            status="success",
            output={
                "value": request.payload.get(
                    "value",
                    1,
                ),
            },
            audit={},
            affects_decision=False,
        )

    def audit(
        self,
        result: CapabilityResult,
    ) -> dict[str, Any]:
        if self.behavior == "audit_error":
            raise RuntimeError(
                "isolated audit failed"
            )

        return {
            "status": result.status,
        }


def build_manifest() -> CapabilityManifest:
    return CapabilityManifest(
        capability_id="CAP-TEST-4001",
        name="Reliability Capability",
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
    behavior: str = "success",
    timeout_seconds: float = 1.0,
) -> CapabilityRuntime:
    registry = CapabilityRegistry()

    registry.register(
        capability=ReliabilityCapability(
            behavior=behavior,
        ),
        manifest=build_manifest(),
    )

    return CapabilityRuntime(
        registry=registry,
        timeout_seconds=timeout_seconds,
        process_isolation=True,
    )


def build_request(
    *,
    request_id: str = "REQ-ISOLATION-RELIABILITY-0001",
) -> CapabilityRequest:
    return CapabilityRequest(
        request_id=request_id,
        payload={
            "value": 10,
        },
        context={
            "execution_mode": "shadow",
        },
    )


def test_isolated_validation_error_is_preserved():
    execution = build_runtime(
        behavior="validation_error",
    ).invoke(
        capability_id="CAP-TEST-4001",
        request=build_request(),
    )

    assert execution.result.status == "error"
    assert execution.error.error_type == (
        "validation_error"
    )
    assert execution.error.stage == "validate"
    assert "isolated validation failed" in (
        execution.error.message
    )


def test_isolated_execution_error_is_preserved():
    execution = build_runtime(
        behavior="execution_error",
    ).invoke(
        capability_id="CAP-TEST-4001",
        request=build_request(),
    )

    assert execution.error.error_type == (
        "execution_error"
    )
    assert execution.error.stage == "execute"


def test_isolated_audit_error_is_preserved():
    execution = build_runtime(
        behavior="audit_error",
    ).invoke(
        capability_id="CAP-TEST-4001",
        request=build_request(),
    )

    assert execution.error.error_type == "audit_error"
    assert execution.error.stage == "audit"


def test_isolated_wrong_result_id_is_rejected():
    execution = build_runtime(
        behavior="wrong_id",
    ).invoke(
        capability_id="CAP-TEST-4001",
        request=build_request(),
    )

    assert execution.error.error_type == (
        "result_integrity_error"
    )
    assert execution.error.stage == "runtime"


def test_worker_crash_returns_worker_error():
    execution = build_runtime(
        behavior="crash",
    ).invoke(
        capability_id="CAP-TEST-4001",
        request=build_request(),
    )

    assert execution.result.status == "error"
    assert execution.error.error_type == (
        "worker_error"
    )
    assert execution.error.stage == "runtime"
    assert execution.error.retryable is True


def test_repeated_isolated_execution_has_no_false_worker_errors():
    runtime = build_runtime()

    for index in range(100):
        execution = runtime.invoke(
            capability_id="CAP-TEST-4001",
            request=build_request(
                request_id=(
                    f"REQ-ISOLATION-REPEAT-{index:04d}"
                ),
            ),
        )

        assert execution.result.status == "success"
        assert execution.error is None


def test_timeout_leaves_no_new_active_worker():
    before = {
        process.pid
        for process in multiprocessing.active_children()
        if process.pid is not None
    }

    runtime = build_runtime(
        behavior="success",
        timeout_seconds=0.05,
    )

    runtime._registry.get(
        "CAP-TEST-4001"
    ).capability.behavior = "slow"

    capability = runtime._registry.get(
        "CAP-TEST-4001"
    ).capability

    original_execute = capability.execute

    def slow_execute(
        request: CapabilityRequest,
    ) -> CapabilityResult:
        sleep(2)
        return original_execute(request)

    capability.execute = slow_execute

    execution = runtime.invoke(
        capability_id="CAP-TEST-4001",
        request=build_request(),
    )

    sleep(0.1)

    after = {
        process.pid
        for process in multiprocessing.active_children()
        if process.pid is not None
    }

    assert execution.error.error_type == "timeout_error"
    assert after - before == set()
