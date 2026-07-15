from copy import deepcopy

import pytest

from app.capabilities.contracts import (
    CAPABILITY_ABI_VERSION,
    CapabilityRequest,
    CapabilityResult,
)
from app.capabilities.knowledge.capability import (
    KNOWLEDGE_CANDIDATE_CAPABILITY_ID,
    KnowledgeCandidateCapability,
)
from app.knowledge.bootstrap import (
    build_default_registry,
)


def build_capability() -> KnowledgeCandidateCapability:
    return KnowledgeCandidateCapability(
        registry=build_default_registry(),
    )


def build_request(
    *,
    domain: str = "transformer",
) -> CapabilityRequest:
    return CapabilityRequest(
        request_id="REQ-KNOWLEDGE-0001",
        payload={
            "domain": domain,
        },
        context={
            "execution_mode": "shadow",
        },
    )


def test_capability_metadata_matches_abi_contract():
    capability = build_capability()

    metadata = capability.metadata()

    assert metadata.capability_id == (
        KNOWLEDGE_CANDIDATE_CAPABILITY_ID
    )
    assert metadata.name == (
        "Knowledge Candidate Generator"
    )
    assert metadata.version == "1.0.0"
    assert metadata.abi_version == (
        CAPABILITY_ABI_VERSION
    )
    assert metadata.shadow_only is True
    assert metadata.affects_decision is False


def test_capability_validate_accepts_valid_request():
    capability = build_capability()
    request = build_request()

    assert capability.validate(request) is None


def test_capability_validate_rejects_missing_domain():
    capability = build_capability()

    request = CapabilityRequest(
        request_id="REQ-KNOWLEDGE-0002",
        payload={},
        context={
            "execution_mode": "shadow",
        },
    )

    with pytest.raises(
        ValueError,
        match="domain",
    ):
        capability.validate(request)


def test_capability_validate_rejects_non_shadow_mode():
    capability = build_capability()

    request = CapabilityRequest(
        request_id="REQ-KNOWLEDGE-0003",
        payload={
            "domain": "transformer",
        },
        context={
            "execution_mode": "active",
        },
    )

    with pytest.raises(
        ValueError,
        match="shadow",
    ):
        capability.validate(request)


def test_capability_execute_returns_capability_result():
    capability = build_capability()

    result = capability.execute(
        build_request()
    )

    assert isinstance(result, CapabilityResult)
    assert result.capability_id == (
        KNOWLEDGE_CANDIDATE_CAPABILITY_ID
    )
    assert result.status == "success"
    assert result.affects_decision is False


def test_capability_execute_serializes_candidate_result():
    capability = build_capability()

    result = capability.execute(
        build_request()
    )

    candidate_result = result.output[
        "knowledge_candidate_result"
    ]

    assert candidate_result["candidate_count"] == 3
    assert candidate_result["shadow_only"] is True
    assert candidate_result["affects_decision"] is False

    assert tuple(
        item["knowledge_id"]
        for item in candidate_result["candidates"]
    ) == (
        "TR-EKO-0001",
        "TR-EKO-0002",
        "TR-EKO-0003",
    )


def test_capability_execute_handles_unknown_domain():
    capability = build_capability()

    result = capability.execute(
        build_request(
            domain="generator",
        )
    )

    candidate_result = result.output[
        "knowledge_candidate_result"
    ]

    assert candidate_result["candidates"] == ()
    assert candidate_result["candidate_count"] == 0
    assert result.status == "success"


def test_capability_execute_does_not_mutate_request():
    capability = build_capability()
    request = build_request()

    before = deepcopy(
        request.model_dump()
    )

    capability.execute(request)

    assert request.model_dump() == before


def test_capability_execute_does_not_mutate_registry():
    registry = build_default_registry()
    before = registry.all()

    capability = KnowledgeCandidateCapability(
        registry=registry,
    )

    capability.execute(
        build_request()
    )

    assert registry.all() == before


def test_capability_audit_returns_descriptive_record():
    capability = build_capability()

    result = capability.execute(
        build_request()
    )
    audit = capability.audit(result)

    assert audit == {
        "capability_id": (
            KNOWLEDGE_CANDIDATE_CAPABILITY_ID
        ),
        "status": "success",
        "candidate_count": 3,
        "shadow_only": True,
        "affects_decision": False,
    }


def test_capability_result_contains_embedded_audit_summary():
    capability = build_capability()

    result = capability.execute(
        build_request()
    )

    assert result.audit == {
        "execution_mode": "shadow",
        "domain": "transformer",
        "candidate_count": 3,
        "affects_decision": False,
    }


def test_capability_audit_rejects_foreign_result():
    capability = build_capability()

    foreign_result = CapabilityResult(
        capability_id="CAP-TEST-9999",
        status="success",
        output={},
        audit={},
        affects_decision=False,
    )

    with pytest.raises(
        ValueError,
        match="capability_id",
    ):
        capability.audit(
            foreign_result
        )


def test_capability_execution_remains_shadow_only():
    capability = build_capability()

    result = capability.execute(
        build_request()
    )
    audit = capability.audit(result)

    assert result.affects_decision is False
    assert result.audit["affects_decision"] is False
    assert audit["affects_decision"] is False


def test_capability_returns_new_result_each_time():
    capability = build_capability()
    request = build_request()

    first = capability.execute(request)
    second = capability.execute(request)

    assert first is not second
    assert first == second
