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


def score_evidence_quality(
    available_evidence: list[str],
    missing_required_evidence: list[str],
    unresolved_conflicts: list[dict] | None = None,
) -> dict:
    unresolved_conflicts = unresolved_conflicts or []

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

    conflict_penalty = 0.25 if unresolved_conflicts else 0.0

    quality_score = round(
        max(
            0.0,
            min(
                1.0,
                (0.60 * completeness_score)
                + (0.40 * directness_score)
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

    return {
        "quality_score": quality_score,
        "quality_level": quality_level,
        "completeness_score": round(completeness_score, 2),
        "directness_score": round(directness_score, 2),
        "conflict_penalty": conflict_penalty,
        "available_direct_evidence": available_direct,
        "missing_required_evidence": missing_required_evidence,
        "unresolved_conflict_count": len(unresolved_conflicts),
        "quality_notes": notes,
    }
