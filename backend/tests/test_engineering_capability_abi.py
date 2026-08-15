from typing import Any

import pytest
from pydantic import ValidationError

from app.capabilities.base import (
    EngineeringCapability,
)
from app.capabilities.contracts import (
    CAPABILITY_ABI_VERSION,
    CapabilityMetadata,
    CapabilityRequest,
    CapabilityResult,
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
        if "value" not in request.payload:
            raise ValueError(
                "value is required."
            )

    def execute(
        self,
        request: CapabilityRequest,
    ) -> CapabilityResult:
        self.validate(request)

        return CapabilityResult(
            capability_id=self.metadata().capability_id,
            status="success",
            output={
                "value": request.payload["value"],
            },
            audit={
                "validated": True,
            },
            affects_decision=False,
        )

    def audit(
        self,
        result: CapabilityResult,
    ) -> dict[str, Any]:
        return {
            "capability_id": result.capability_id,
            "status": result.status,
            "affects_decision": (
                result.affects_decision
            ),
        }


def build_request() -> CapabilityRequest:
    return CapabilityRequest(
        request_id="REQ-0001",
        payload={
            "value": 10,
        },
        context={
            "mode": "shadow",
        },
    )


def test_capability_abi_version_is_explicit():
    assert CAPABILITY_ABI_VERSION == "1.0"


def test_capability_request_accepts_valid_structure():
    request = build_request()

    assert request.request_id == "REQ-0001"
    assert request.payload == {
        "value": 10,
    }
    assert request.context == {
        "mode": "shadow",
    }


def test_capability_metadata_accepts_valid_structure():
    metadata = ExampleCapability().metadata()

    assert metadata.capability_id == "CAP-TEST-0001"
    assert metadata.version == "1.0.0"
    assert metadata.abi_version == "1.0"
    assert metadata.shadow_only is True
    assert metadata.affects_decision is False


def test_capability_executes_through_abi_contract():
    capability = ExampleCapability()
    request = build_request()

    capability.validate(request)
    result = capability.execute(request)
    audit = capability.audit(result)

    assert result.status == "success"
    assert result.output == {
        "value": 10,
    }
    assert result.affects_decision is False

    assert audit == {
        "capability_id": "CAP-TEST-0001",
        "status": "success",
        "affects_decision": False,
    }


def test_capability_validation_failure_is_explicit():
    capability = ExampleCapability()

    request = CapabilityRequest(
        request_id="REQ-0002",
        payload={},
    )

    with pytest.raises(
        ValueError,
        match="value is required",
    ):
        capability.validate(request)


def test_capability_contract_models_are_read_only():
    request = build_request()
    metadata = ExampleCapability().metadata()
    result = ExampleCapability().execute(
        request
    )

    with pytest.raises(ValidationError):
        request.request_id = "REQ-CHANGED"

    with pytest.raises(ValidationError):
        metadata.version = "2.0.0"

    with pytest.raises(ValidationError):
        result.status = "error"


def test_capability_contract_models_forbid_unknown_fields():
    with pytest.raises(ValidationError):
        CapabilityRequest(
            request_id="REQ-0003",
            payload={},
            unexpected=True,
        )

    with pytest.raises(ValidationError):
        CapabilityMetadata(
            capability_id="CAP-TEST-0002",
            name="Invalid Metadata",
            version="1.0.0",
            abi_version="1.0",
            shadow_only=True,
            affects_decision=False,
            unexpected=True,
        )


@pytest.mark.parametrize(
    "invalid_id",
    [
        "",
        "TEST-0001",
        "cap-test-0001",
        "CAP-1",
    ],
)
def test_capability_metadata_rejects_invalid_id(
    invalid_id: str,
):
    with pytest.raises(ValidationError):
        CapabilityMetadata(
            capability_id=invalid_id,
            name="Invalid Capability",
            version="1.0.0",
            abi_version="1.0",
            shadow_only=True,
            affects_decision=False,
        )


@pytest.mark.parametrize(
    "invalid_version",
    [
        "",
        "1",
        "1.0",
        "v1.0.0",
        "1.0.0.0",
    ],
)
def test_capability_metadata_rejects_invalid_version(
    invalid_version: str,
):
    with pytest.raises(ValidationError):
        CapabilityMetadata(
            capability_id="CAP-TEST-0003",
            name="Invalid Capability",
            version=invalid_version,
            abi_version="1.0",
            shadow_only=True,
            affects_decision=False,
        )


def test_capability_result_rejects_invalid_status():
    with pytest.raises(ValidationError):
        CapabilityResult(
            capability_id="CAP-TEST-0001",
            status="unknown",
            output={},
            audit={},
            affects_decision=False,
        )


def test_capability_result_preserves_payloads_without_mutating_request():
    capability = ExampleCapability()
    request = build_request()

    request_before = request.model_dump()
    result = capability.execute(request)

    assert request.model_dump() == request_before
    assert result.output is not request.payload


def test_capability_metadata_rejects_non_shadow_mode():
    with pytest.raises(ValidationError):
        CapabilityMetadata(
            capability_id="CAP-TEST-0004",
            name="Non Shadow Capability",
            version="1.0.0",
            abi_version=CAPABILITY_ABI_VERSION,
            shadow_only=False,
            affects_decision=False,
        )