from __future__ import annotations

import pytest

from app.capabilities.base import EngineeringCapability
from app.capabilities.contracts import (
    CAPABILITY_ABI_VERSION,
    CapabilityMetadata,
    CapabilityRequest,
    CapabilityResult,
)
from app.capabilities.foundation_adapter import (
    CAPABILITY_REQUEST_RESOURCE_KEY,
    CapabilityFoundationAdapter,
)
from app.capabilities.manifest import CapabilityManifest
from app.capabilities.registry import CapabilityRegistry
from app.capabilities.runtime import CapabilityRuntime
from app.foundation.context import ExecutionContext
from app.foundation.interfaces import Engine
from app.foundation.types import ExecutionStatus


class SuccessfulCapability(EngineeringCapability):
    def metadata(self) -> CapabilityMetadata:
        return CapabilityMetadata(
            capability_id="CAP-TEST-2001",
            name="Adapter Test Capability",
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
            raise ValueError(
                "shadow mode is required"
            )

    def execute(
        self,
        request: CapabilityRequest,
    ) -> CapabilityResult:
        return CapabilityResult(
            capability_id="CAP-TEST-2001",
            status="success",
            output={
                "value": request.payload.get(
                    "value"
                ),
            },
            audit={},
            affects_decision=False,
        )

    def audit(
        self,
        result: CapabilityResult,
    ) -> dict[str, object]:
        return {
            "audited": True,
            "status": result.status,
        }


def build_manifest() -> CapabilityManifest:
    return CapabilityManifest(
        capability_id="CAP-TEST-2001",
        name="Adapter Test Capability",
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
        manifest=build_manifest(),
    )

    return CapabilityRuntime(
        registry=registry,
    )


def build_request(
    *,
    mode: str = "shadow",
) -> CapabilityRequest:
    return CapabilityRequest(
        request_id="REQ-ADAPTER-0001",
        payload={
            "value": 42,
        },
        context={
            "execution_mode": mode,
        },
    )


def build_adapter() -> CapabilityFoundationAdapter:
    return CapabilityFoundationAdapter(
        capability_id="CAP-TEST-2001",
        runtime=build_runtime(),
        metadata=SuccessfulCapability().metadata(),
    )


def test_capability_adapter_satisfies_engine_contract():
    engine: Engine = build_adapter()

    assert engine.metadata.name


def test_capability_adapter_metadata_valid():
    adapter = build_adapter()

    assert adapter.metadata.name == (
        "capability:CAP-TEST-2001"
    )
    assert adapter.metadata.category == (
        "capability"
    )
    assert adapter.metadata.version == (
        "1.0.0"
    )


def test_capability_adapter_success_mapping():
    adapter = build_adapter()

    context = ExecutionContext(
        resources={
            CAPABILITY_REQUEST_RESOURCE_KEY:
                build_request(),
        }
    )

    result = adapter.execute(
        context
    )

    assert (
        result.status
        == ExecutionStatus.SUCCESS
    )

    assert result.payload == {
        "value": 42,
    }

    assert result.diagnostics.execution_time_ms >= 0

    assert result.diagnostics.traceability == (
        "REQ-ADAPTER-0001",
    )

    assert (
        result.metadata["capability_id"]
        == "CAP-TEST-2001"
    )

    assert result.shadow_only is True
    assert result.affects_reasoning is False
    assert result.affects_decision is False


def test_capability_adapter_failure_mapping():
    adapter = build_adapter()

    context = ExecutionContext(
        resources={
            CAPABILITY_REQUEST_RESOURCE_KEY:
                build_request(
                    mode="active",
                ),
        }
    )

    result = adapter.execute(
        context
    )

    assert (
        result.status
        == ExecutionStatus.FAILED
    )

    assert result.payload == {}

    assert result.diagnostics.errors

    assert (
        result.diagnostics.metadata[
            "error_type"
        ]
        == "shadow_mode_required"
    )

    assert (
        result.diagnostics.metadata[
            "retryable"
        ]
        is False
    )

    assert result.shadow_only is True
    assert result.affects_reasoning is False
    assert result.affects_decision is False


def test_capability_adapter_missing_resources_key():
    adapter = build_adapter()

    with pytest.raises(
        Exception,
    ):
        adapter.execute(
            ExecutionContext()
        )


def test_capability_adapter_rejects_wrong_resource_type():
    adapter = build_adapter()

    context = ExecutionContext(
        resources={
            CAPABILITY_REQUEST_RESOURCE_KEY:
                {"not": "a CapabilityRequest"},
        }
    )

    with pytest.raises(
        Exception,
    ):
        adapter.execute(
            context
        )


def test_capability_adapter_preserves_request():
    adapter = build_adapter()
    request = build_request()
    before = request.model_dump()

    context = ExecutionContext(
        resources={
            CAPABILITY_REQUEST_RESOURCE_KEY:
                request,
        }
    )

    adapter.execute(
        context
    )

    assert request.model_dump() == before


def test_capability_adapter_uses_runtime_failure_semantics():
    adapter = CapabilityFoundationAdapter(
        capability_id="CAP-TEST-9999",
        runtime=build_runtime(),
        metadata=CapabilityMetadata(
            capability_id="CAP-TEST-9999",
            name="Missing Capability",
            version="1.0.0",
            abi_version=CAPABILITY_ABI_VERSION,
            shadow_only=True,
            affects_decision=False,
        ),
    )

    context = ExecutionContext(
        resources={
            CAPABILITY_REQUEST_RESOURCE_KEY:
                build_request(),
        }
    )

    result = adapter.execute(
        context
    )

    assert (
        result.status
        == ExecutionStatus.FAILED
    )

    assert (
        result.diagnostics.metadata[
            "error_type"
        ]
        == "not_found"
    )


def test_capability_adapter_exposes_audit_outside_payload():
    adapter = build_adapter()

    context = ExecutionContext(
        resources={
            CAPABILITY_REQUEST_RESOURCE_KEY:
                build_request(),
        }
    )

    result = adapter.execute(
        context
    )

    assert result.payload == {
        "value": 42,
    }

    assert "audit" not in result.payload

    assert (
        "audit"
        in result.metadata
        or "audit"
        in result.diagnostics.metadata
    )