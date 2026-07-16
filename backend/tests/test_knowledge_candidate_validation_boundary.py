from unittest.mock import Mock

from app.capabilities.contracts import (
    CapabilityRequest,
)
from app.capabilities.knowledge.capability import (
    KnowledgeCandidateCapability,
)
from app.knowledge.bootstrap import (
    build_default_registry,
)


def build_request() -> CapabilityRequest:
    return CapabilityRequest(
        request_id="REQ-VALIDATION-BOUNDARY-0001",
        payload={
            "domain": "transformer",
        },
        context={
            "execution_mode": "shadow",
        },
    )


def test_validate_does_not_generate_candidates():
    capability = KnowledgeCandidateCapability(
        registry=build_default_registry(),
    )

    capability._generator.generate = Mock()

    capability.validate(
        build_request()
    )

    capability._generator.generate.assert_not_called()


def test_execute_generates_candidates_exactly_once():
    capability = KnowledgeCandidateCapability(
        registry=build_default_registry(),
    )

    original_generate = (
        capability._generator.generate
    )
    capability._generator.generate = Mock(
        wraps=original_generate,
    )

    result = capability.execute(
        build_request()
    )

    capability._generator.generate.assert_called_once_with(
        domain="transformer",
    )

    assert result.status == "success"
    assert result.affects_decision is False
    assert result.output[
        "knowledge_candidate_result"
    ]["candidate_count"] == 3
