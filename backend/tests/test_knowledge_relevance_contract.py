import pytest
from pydantic import ValidationError

from app.capabilities.knowledge_relevance import (
    KnowledgeRelevanceRequest,
    KnowledgeRelevanceResult,
)


def build_request() -> KnowledgeRelevanceRequest:
    return KnowledgeRelevanceRequest(
        domain="transformer",
        asset_type="power_transformer",
        available_evidence=("87T pickup",),
        missing_evidence=("DGA result",),
        investigation_stage="hypothesis_evaluation",
        max_results=3,
    )


def test_request_accepts_valid_structure():
    request = build_request()

    assert request.domain == "transformer"
    assert request.asset_type == "power_transformer"
    assert request.available_evidence == ("87T pickup",)
    assert request.missing_evidence == ("DGA result",)
    assert request.investigation_stage == "hypothesis_evaluation"
    assert request.max_results == 3


@pytest.mark.parametrize(
    "field_name",
    ["domain", "asset_type", "investigation_stage"],
)
def test_request_rejects_blank_required_strings(field_name: str):
    payload = build_request().model_dump()
    payload[field_name] = "   "

    with pytest.raises(ValidationError):
        KnowledgeRelevanceRequest(**payload)


@pytest.mark.parametrize("max_results", [0, -1, -100])
def test_request_rejects_non_positive_max_results(max_results: int):
    payload = build_request().model_dump()
    payload["max_results"] = max_results

    with pytest.raises(ValidationError):
        KnowledgeRelevanceRequest(**payload)


def test_result_accepts_ranked_reference_only_output():
    result = KnowledgeRelevanceResult(
        selected_ids=("TR-EKO-0001", "TR-EKO-0002"),
        scores=(0.95, 0.70),
        selection_reasons=(
            "domain and evidence match",
            "asset and investigation stage match",
        ),
        ignored_ids=("TR-EKO-0003",),
    )

    assert result.selected_ids == (
        "TR-EKO-0001",
        "TR-EKO-0002",
    )
    assert result.scores == (0.95, 0.70)
    assert result.ignored_ids == ("TR-EKO-0003",)

    dumped = result.model_dump()

    assert "content" not in dumped
    assert "text" not in dumped
    assert "documents" not in dumped


def test_result_rejects_out_of_range_score():
    with pytest.raises(ValidationError):
        KnowledgeRelevanceResult(
            selected_ids=("TR-EKO-0001",),
            scores=(1.1,),
            selection_reasons=("domain match",),
            ignored_ids=(),
        )


def test_result_rejects_unsorted_scores():
    with pytest.raises(ValidationError):
        KnowledgeRelevanceResult(
            selected_ids=("TR-EKO-0001", "TR-EKO-0002"),
            scores=(0.60, 0.90),
            selection_reasons=("partial match", "strong match"),
            ignored_ids=(),
        )


def test_result_rejects_mismatched_output_lengths():
    with pytest.raises(ValidationError):
        KnowledgeRelevanceResult(
            selected_ids=("TR-EKO-0001", "TR-EKO-0002"),
            scores=(0.90,),
            selection_reasons=("domain match", "asset match"),
            ignored_ids=(),
        )


def test_result_rejects_duplicate_selected_ids():
    with pytest.raises(ValidationError):
        KnowledgeRelevanceResult(
            selected_ids=("TR-EKO-0001", "TR-EKO-0001"),
            scores=(0.90, 0.80),
            selection_reasons=("domain match", "asset match"),
            ignored_ids=(),
        )


def test_result_rejects_selected_id_in_ignored_ids():
    with pytest.raises(ValidationError):
        KnowledgeRelevanceResult(
            selected_ids=("TR-EKO-0001",),
            scores=(0.90,),
            selection_reasons=("domain match",),
            ignored_ids=("TR-EKO-0001",),
        )
