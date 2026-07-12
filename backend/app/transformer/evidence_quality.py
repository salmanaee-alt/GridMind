from __future__ import annotations


DIRECT_EVIDENCE = {
    "Relay event report",
    "COMTRADE waveform",
    "Differential relay targets",
    "DGA report",
    "Buchholz relay status",
    "Visual inspection",
}

CONTEXT_EVIDENCE = {
    "HV/LV breaker status",
    "Oil temperature",
    "Load before trip",
    "Recent maintenance history",
}

HIGH_RELIABILITY_SOURCES = {
    "relay",
    "comtrade",
    "lab",
}

MEDIUM_RELIABILITY_SOURCES = {
    "field_inspection",
    "scada",
    "maintenance",
}

LOW_RELIABILITY_SOURCES = {
    "operator",
    "unknown",
}

TIMESTAMP_RELATION_SCORES = {
    "during_event": 1.0,
    "after_event": 0.8,
    "before_event": 0.6,
    "not_applicable": 0.5,
    "unknown": 0.4,
}


def score_evidence_quality(
    available_evidence: list[str],
    missing_required_evidence: list[str],
    unresolved_conflicts: list[dict] | None = None,
    evidence_metadata: list[dict] | None = None,
) -> dict:
    unresolved_conflicts = unresolved_conflicts or []
    evidence_metadata = evidence_metadata or []

    metadata_names = [
        item.get("evidence_name")
        for item in evidence_metadata
    ]

    if len(metadata_names) != len(set(metadata_names)):
        raise ValueError(
            "Evidence metadata requires unique evidence_name values."
        )

    available_evidence = list(
        dict.fromkeys(available_evidence)
    )

    total_expected = len(set(available_evidence + missing_required_evidence))

    if total_expected == 0:
        completeness_score = 0.0
    else:
        completeness_score = len(set(available_evidence)) / total_expected

    available_direct = [
        item for item in available_evidence
        if item in DIRECT_EVIDENCE
    ]

    expected_direct = [
        item for item in DIRECT_EVIDENCE
        if item in available_evidence or item in missing_required_evidence
    ]

    if not expected_direct:
        directness_score = 0.0
    else:
        directness_score = len(available_direct) / len(expected_direct)

    metadata_score = _score_metadata_quality(
        available_evidence=available_evidence,
        evidence_metadata=evidence_metadata,
    )

    evidence_weight_details = _build_evidence_weight_details(
        available_evidence=available_evidence,
        evidence_metadata=evidence_metadata,
    )

    conflict_penalty = 0.25 if unresolved_conflicts else 0.0

    quality_score = round(
        max(
            0.0,
            min(
                1.0,
                (0.45 * completeness_score)
                + (0.30 * directness_score)
                + (0.25 * metadata_score["metadata_score"])
                - conflict_penalty,
            ),
        ),
        2,
    )

    if quality_score >= 0.75:
        quality_level = "high"
    elif quality_score >= 0.45:
        quality_level = "medium"
    else:
        quality_level = "low"

    notes: list[str] = []

    if missing_required_evidence:
        notes.append("Some required evidence is missing.")

    if unresolved_conflicts:
        notes.append("Evidence conflicts reduce overall evidence quality.")

    if available_direct:
        notes.append("Direct diagnostic evidence is available.")

    if not available_direct:
        notes.append("No direct diagnostic evidence is available.")

    notes.extend(metadata_score["metadata_quality_notes"])

    return {
        "quality_score": quality_score,
        "quality_level": quality_level,
        "completeness_score": round(completeness_score, 2),
        "directness_score": round(directness_score, 2),
        "metadata_score": metadata_score["metadata_score"],
        "verified_evidence_ratio": metadata_score["verified_evidence_ratio"],
        "source_reliability_score": metadata_score["source_reliability_score"],
        "timestamp_relation_score": metadata_score["timestamp_relation_score"],
        "freshness_score": metadata_score["freshness_score"],
        "evidence_weight_details": evidence_weight_details,
        "weight_model": "metadata_quality_v0.1",
        "weight_model_is_calibrated_probability": False,
        "conflict_penalty": conflict_penalty,
        "available_direct_evidence": available_direct,
        "missing_required_evidence": missing_required_evidence,
        "unresolved_conflict_count": len(unresolved_conflicts),
        "metadata_quality_notes": metadata_score["metadata_quality_notes"],
        "quality_notes": notes,
    }


def _score_metadata_quality(
    available_evidence: list[str],
    evidence_metadata: list[dict],
) -> dict:
    available_set = set(available_evidence)

    relevant_metadata = [
        item for item in evidence_metadata
        if item.get("evidence_name") in available_set
    ]

    if not available_evidence:
        verified_evidence_ratio = 0.0
    else:
        verified_count = sum(
            1 for item in relevant_metadata
            if item.get("verified") is True
        )
        verified_evidence_ratio = verified_count / len(set(available_evidence))

    if not relevant_metadata:
        source_reliability_score = 0.0
        timestamp_relation_score = 0.0
        freshness_score = 0.0
    else:
        source_scores = [
            _source_reliability_value(item.get("source_type", "unknown"))
            for item in relevant_metadata
        ]
        timestamp_scores = [
            _timestamp_relation_value(item.get("timestamp_relation", "unknown"))
            for item in relevant_metadata
        ]
        freshness_scores = [
            _freshness_value(item.get("evidence_age_days"))
            for item in relevant_metadata
        ]

        source_reliability_score = sum(source_scores) / len(source_scores)
        timestamp_relation_score = sum(timestamp_scores) / len(timestamp_scores)
        freshness_score = sum(freshness_scores) / len(freshness_scores)

    metadata_score = round(
        max(
            0.0,
            min(
                1.0,
                (0.35 * verified_evidence_ratio)
                + (0.30 * source_reliability_score)
                + (0.20 * timestamp_relation_score)
                + (0.15 * freshness_score),
            ),
        ),
        2,
    )

    notes: list[str] = []

    if not evidence_metadata:
        notes.append("No evidence metadata was provided.")

    if evidence_metadata and not relevant_metadata:
        notes.append("Evidence metadata was provided but did not match available evidence names.")

    if relevant_metadata:
        notes.append("Evidence metadata is available for some diagnostic inputs.")

    if verified_evidence_ratio < 0.5:
        notes.append("Less than half of available evidence is marked as verified.")

    if source_reliability_score >= 0.75:
        notes.append("Evidence sources have high reliability.")
    elif source_reliability_score > 0:
        notes.append("Evidence sources have mixed or moderate reliability.")

    if timestamp_relation_score >= 0.75:
        notes.append("Evidence timing is strongly aligned with the event.")
    elif timestamp_relation_score > 0:
        notes.append("Evidence timing has mixed or moderate alignment with the event.")

    if freshness_score >= 0.75:
        notes.append("Evidence is recent.")
    elif freshness_score > 0:
        notes.append("Evidence freshness is mixed, old, or unknown.")

    return {
        "metadata_score": metadata_score,
        "verified_evidence_ratio": round(verified_evidence_ratio, 2),
        "source_reliability_score": round(source_reliability_score, 2),
        "timestamp_relation_score": round(timestamp_relation_score, 2),
        "freshness_score": round(freshness_score, 2),
        "metadata_quality_notes": notes,
    }


def _build_evidence_weight_details(
    available_evidence: list[str],
    evidence_metadata: list[dict],
) -> list[dict]:
    metadata_by_name: dict[str, dict] = {}

    for item in evidence_metadata:
        evidence_name = item.get("evidence_name")

        if evidence_name and evidence_name not in metadata_by_name:
            metadata_by_name[evidence_name] = item

    weight_details: list[dict] = []

    for evidence_name in sorted(set(available_evidence)):
        metadata = metadata_by_name.get(evidence_name)

        if metadata is None:
            verification_factor = 0.0
            source_reliability = 0.0
            timing_factor = 0.0
            freshness_factor = 0.0
            metadata_available = False
        else:
            verification_factor = (
                1.0 if metadata.get("verified") is True else 0.0
            )
            source_reliability = _source_reliability_value(
                metadata.get("source_type", "unknown")
            )
            timing_factor = _timestamp_relation_value(
                metadata.get("timestamp_relation", "unknown")
            )
            freshness_factor = _freshness_value(
                metadata.get("evidence_age_days")
            )
            metadata_available = True

        raw_weight = round(
            (0.35 * verification_factor)
            + (0.30 * source_reliability)
            + (0.20 * timing_factor)
            + (0.15 * freshness_factor),
            2,
        )

        weight_details.append({
            "evidence_name": evidence_name,
            "raw_weight": raw_weight,
            "metadata_available": metadata_available,
            "weight_factors": {
                "verification_factor": verification_factor,
                "source_reliability": source_reliability,
                "timing_factor": timing_factor,
                "freshness_factor": freshness_factor,
            },
        })

    return weight_details


def _source_reliability_value(source_type: str) -> float:
    if source_type in HIGH_RELIABILITY_SOURCES:
        return 1.0

    if source_type in MEDIUM_RELIABILITY_SOURCES:
        return 0.7

    if source_type in LOW_RELIABILITY_SOURCES:
        return 0.4

    return 0.4


def _timestamp_relation_value(timestamp_relation: str) -> float:
    return TIMESTAMP_RELATION_SCORES.get(timestamp_relation, 0.4)


def _freshness_value(evidence_age_days: int | None) -> float:
    if evidence_age_days is None:
        return 0.4

    if evidence_age_days <= 7:
        return 1.0

    if evidence_age_days <= 30:
        return 0.7

    if evidence_age_days <= 90:
        return 0.4

    return 0.2
