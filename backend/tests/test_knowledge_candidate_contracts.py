import pytest
from pydantic import ValidationError

from app.capabilities.knowledge.contracts import (
    CandidateReason,
    CandidateSource,
    KnowledgeCandidate,
    KnowledgeCandidateResult,
)


def build_candidate() -> KnowledgeCandidate:
    return KnowledgeCandidate(
        knowledge_id="TR-EKO-0001",
        source=CandidateSource.REGISTRY,
        reason=CandidateReason(
            code="domain_match",
            description=(
                "Knowledge object belongs to the transformer domain."
            ),
        ),
        shadow_only=True,
        affects_decision=False,
    )


def build_result() -> KnowledgeCandidateResult:
    return KnowledgeCandidateResult(
        candidates=(
            build_candidate(),
        ),
        candidate_count=1,
        shadow_only=True,
        affects_decision=False,
    )


def test_candidate_accepts_valid_structure():
    candidate = build_candidate()

    assert candidate.knowledge_id == "TR-EKO-0001"
    assert candidate.source == CandidateSource.REGISTRY
    assert candidate.reason.code == "domain_match"
    assert candidate.shadow_only is True
    assert candidate.affects_decision is False


def test_candidate_result_accepts_valid_structure():
    result = build_result()

    assert result.candidate_count == 1
    assert len(result.candidates) == 1
    assert result.candidates[0] == build_candidate()
    assert result.shadow_only is True
    assert result.affects_decision is False


def test_candidate_models_are_read_only():
    candidate = build_candidate()
    result = build_result()

    with pytest.raises(ValidationError):
        candidate.knowledge_id = "TR-EKO-9999"

    with pytest.raises(ValidationError):
        candidate.reason.code = "changed"

    with pytest.raises(ValidationError):
        result.candidate_count = 2


def test_candidate_models_forbid_unknown_fields():
    payload = build_candidate().model_dump()
    payload["unexpected"] = True

    with pytest.raises(ValidationError):
        KnowledgeCandidate(**payload)

    result_payload = build_result().model_dump()
    result_payload["unexpected"] = True

    with pytest.raises(ValidationError):
        KnowledgeCandidateResult(**result_payload)


@pytest.mark.parametrize(
    "invalid_id",
    [
        "",
        "invalid",
        "TR-0001",
        "tr-EKO-0001",
    ],
)
def test_candidate_rejects_invalid_knowledge_id(
    invalid_id: str,
):
    payload = build_candidate().model_dump()
    payload["knowledge_id"] = invalid_id

    with pytest.raises(ValidationError):
        KnowledgeCandidate(**payload)


@pytest.mark.parametrize(
    "invalid_code",
    [
        "",
        "Domain Match",
        "domain-match",
        "domain/match",
    ],
)
def test_candidate_reason_rejects_invalid_code(
    invalid_code: str,
):
    with pytest.raises(ValidationError):
        CandidateReason(
            code=invalid_code,
            description="Candidate reason.",
        )


def test_candidate_reason_rejects_blank_description():
    with pytest.raises(ValidationError):
        CandidateReason(
            code="domain_match",
            description="   ",
        )


def test_candidate_rejects_decision_affecting_state():
    payload = build_candidate().model_dump()
    payload["affects_decision"] = True

    with pytest.raises(ValidationError):
        KnowledgeCandidate(**payload)


def test_result_rejects_decision_affecting_state():
    payload = build_result().model_dump()
    payload["affects_decision"] = True

    with pytest.raises(ValidationError):
        KnowledgeCandidateResult(**payload)


def test_result_rejects_incorrect_candidate_count():
    payload = build_result().model_dump()
    payload["candidate_count"] = 2

    with pytest.raises(
        ValidationError,
        match="candidate_count",
    ):
        KnowledgeCandidateResult(**payload)


def test_result_accepts_empty_candidate_collection():
    result = KnowledgeCandidateResult(
        candidates=(),
        candidate_count=0,
        shadow_only=True,
        affects_decision=False,
    )

    assert result.candidates == ()
    assert result.candidate_count == 0


def test_candidate_collection_is_a_tuple():
    result = build_result()

    assert isinstance(result.candidates, tuple)


def test_candidate_serialization_is_stable():
    candidate = build_candidate()
    result = build_result()

    candidate_dump = candidate.model_dump()
    result_dump = result.model_dump()

    assert KnowledgeCandidate(
        **candidate_dump
    ) == candidate

    assert KnowledgeCandidateResult(
        **result_dump
    ) == result


def test_result_preserves_candidate_order():
    first = build_candidate()
    second = KnowledgeCandidate(
        knowledge_id="TR-EKO-0002",
        source=CandidateSource.REGISTRY,
        reason=CandidateReason(
            code="domain_match",
            description=(
                "Second transformer knowledge candidate."
            ),
        ),
        shadow_only=True,
        affects_decision=False,
    )

    result = KnowledgeCandidateResult(
        candidates=(
            first,
            second,
        ),
        candidate_count=2,
        shadow_only=True,
        affects_decision=False,
    )

    assert tuple(
        item.knowledge_id
        for item in result.candidates
    ) == (
        "TR-EKO-0001",
        "TR-EKO-0002",
    )
