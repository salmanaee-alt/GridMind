from app.capabilities.knowledge_relevance.scoring import (
    KnowledgeRelevanceCandidate,
    rank_knowledge_candidates,
)
from app.capabilities.knowledge_relevance import (
    KnowledgeRelevanceRequest,
)


def build_request(
    *,
    max_results: int = 3,
) -> KnowledgeRelevanceRequest:
    return KnowledgeRelevanceRequest(
        domain="transformer",
        asset_type="power_transformer",
        available_evidence=(
            "87T pickup",
            "Buchholz alarm",
        ),
        missing_evidence=(
            "DGA result",
        ),
        investigation_stage="hypothesis_evaluation",
        max_results=max_results,
    )


def build_candidates():
    return (
        KnowledgeRelevanceCandidate(
            knowledge_id="TR-EKO-0001",
            domains=("transformer",),
            asset_types=("power_transformer",),
            evidence_terms=(
                "87T pickup",
                "Buchholz alarm",
                "DGA result",
            ),
            investigation_stages=(
                "hypothesis_evaluation",
            ),
        ),
        KnowledgeRelevanceCandidate(
            knowledge_id="TR-EKO-0002",
            domains=("transformer",),
            asset_types=("power_transformer",),
            evidence_terms=("87T pickup",),
            investigation_stages=("initial_triage",),
        ),
        KnowledgeRelevanceCandidate(
            knowledge_id="CB-EKO-0001",
            domains=("circuit_breaker",),
            asset_types=("high_voltage_breaker",),
            evidence_terms=("failed to open",),
            investigation_stages=("hypothesis_evaluation",),
        ),
    )


def test_ranking_prefers_strongest_context_match():
    result = rank_knowledge_candidates(
        request=build_request(),
        candidates=build_candidates(),
    )

    assert result.selected_ids[0] == "TR-EKO-0001"
    assert result.scores[0] > result.scores[1]
    assert "TR-EKO-0001" not in result.ignored_ids


def test_ranking_is_deterministic():
    request = build_request()
    candidates = build_candidates()

    first = rank_knowledge_candidates(
        request=request,
        candidates=candidates,
    )
    second = rank_knowledge_candidates(
        request=request,
        candidates=candidates,
    )

    assert first == second


def test_ranking_respects_max_results():
    result = rank_knowledge_candidates(
        request=build_request(max_results=1),
        candidates=build_candidates(),
    )

    assert len(result.selected_ids) == 1
    assert len(result.scores) == 1
    assert len(result.selection_reasons) == 1
    assert set(result.ignored_ids) == {
        "TR-EKO-0002",
        "CB-EKO-0001",
    }


def test_ranking_uses_stable_id_tie_breaker():
    candidates = (
        KnowledgeRelevanceCandidate(
            knowledge_id="TR-EKO-0002",
            domains=("transformer",),
            asset_types=("power_transformer",),
            evidence_terms=("87T pickup",),
            investigation_stages=("hypothesis_evaluation",),
        ),
        KnowledgeRelevanceCandidate(
            knowledge_id="TR-EKO-0001",
            domains=("transformer",),
            asset_types=("power_transformer",),
            evidence_terms=("87T pickup",),
            investigation_stages=("hypothesis_evaluation",),
        ),
    )

    result = rank_knowledge_candidates(
        request=build_request(max_results=2),
        candidates=candidates,
    )

    assert result.selected_ids == (
        "TR-EKO-0001",
        "TR-EKO-0002",
    )
    assert result.scores[0] == result.scores[1]


def test_ranking_returns_reference_only_output():
    result = rank_knowledge_candidates(
        request=build_request(),
        candidates=build_candidates(),
    )

    dumped = result.model_dump()

    assert "content" not in dumped
    assert "text" not in dumped
    assert "documents" not in dumped
    assert "embeddings" not in dumped


def test_empty_candidates_return_empty_result():
    result = rank_knowledge_candidates(
        request=build_request(),
        candidates=(),
    )

    assert result.selected_ids == ()
    assert result.scores == ()
    assert result.selection_reasons == ()
    assert result.ignored_ids == ()
