from dataclasses import dataclass

from .contracts import (
    KnowledgeRelevanceRequest,
    KnowledgeRelevanceResult,
)


@dataclass(frozen=True)
class KnowledgeRelevanceCandidate:
    knowledge_id: str
    domains: tuple[str, ...]
    asset_types: tuple[str, ...]
    evidence_terms: tuple[str, ...]
    investigation_stages: tuple[str, ...]


@dataclass(frozen=True)
class _RankedCandidate:
    candidate: KnowledgeRelevanceCandidate
    score: float
    reason: str


def _normalize(value: str) -> str:
    return value.strip().casefold()


def _normalized_set(values: tuple[str, ...]) -> set[str]:
    return {
        _normalize(value)
        for value in values
    }


def _score_candidate(
    *,
    request: KnowledgeRelevanceRequest,
    candidate: KnowledgeRelevanceCandidate,
) -> _RankedCandidate:
    score = 0.0
    reasons: list[str] = []

    request_domain = _normalize(request.domain)
    candidate_domains = _normalized_set(candidate.domains)

    if request_domain in candidate_domains:
        score += 0.30
        reasons.append("domain match")

    request_asset_type = _normalize(request.asset_type)
    candidate_asset_types = _normalized_set(
        candidate.asset_types
    )

    if request_asset_type in candidate_asset_types:
        score += 0.25
        reasons.append("asset type match")

    request_stage = _normalize(
        request.investigation_stage
    )
    candidate_stages = _normalized_set(
        candidate.investigation_stages
    )

    if request_stage in candidate_stages:
        score += 0.20
        reasons.append("investigation stage match")

    candidate_evidence = _normalized_set(
        candidate.evidence_terms
    )

    available_matches = (
        _normalized_set(request.available_evidence)
        & candidate_evidence
    )

    if available_matches:
        score += min(
            0.15,
            0.05 * len(available_matches),
        )
        reasons.append(
            f"{len(available_matches)} available evidence match"
        )

    missing_matches = (
        _normalized_set(request.missing_evidence)
        & candidate_evidence
    )

    if missing_matches:
        score += min(
            0.10,
            0.05 * len(missing_matches),
        )
        reasons.append(
            f"{len(missing_matches)} missing evidence match"
        )

    score = round(min(score, 1.0), 4)

    if not reasons:
        reasons.append("no direct context match")

    return _RankedCandidate(
        candidate=candidate,
        score=score,
        reason=", ".join(reasons),
    )


def rank_knowledge_candidates(
    *,
    request: KnowledgeRelevanceRequest,
    candidates: tuple[
        KnowledgeRelevanceCandidate,
        ...,
    ],
) -> KnowledgeRelevanceResult:
    ranked = tuple(
        sorted(
            (
                _score_candidate(
                    request=request,
                    candidate=candidate,
                )
                for candidate in candidates
            ),
            key=lambda item: (
                -item.score,
                item.candidate.knowledge_id,
            ),
        )
    )

    selected = ranked[: request.max_results]
    ignored = ranked[request.max_results :]

    return KnowledgeRelevanceResult(
        selected_ids=tuple(
            item.candidate.knowledge_id
            for item in selected
        ),
        scores=tuple(
            item.score
            for item in selected
        ),
        selection_reasons=tuple(
            item.reason
            for item in selected
        ),
        ignored_ids=tuple(
            item.candidate.knowledge_id
            for item in ignored
        ),
    )
