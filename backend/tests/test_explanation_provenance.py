from app.brain.explanation_provenance import (
    build_explanation_provenance_details,
)


def test_explanation_provenance_tracks_original_sources():
    conflict = {
        "conflict": "Breaker failed to open after trip.",
        "severity": "high",
        "recommended_verification": (
            "Verify breaker position and trip circuit."
        ),
    }

    hypothesis = {
        "supporting_evidence": [
            "Relay target supports differential operation.",
        ],
        "missing_evidence": [
            "DGA report",
        ],
        "conflicts": [
            conflict,
        ],
        "why_supported": [
            "Relay target supports differential operation.",
        ],
        "why_not_confirmed": [
            "DGA report",
            "Breaker failed to open after trip.",
        ],
        "confidence_drivers": [
            "Relay target supports differential operation.",
        ],
        "confidence_limiters": [
            "DGA report",
            "Breaker failed to open after trip.",
        ],
        "evidence_that_would_change_decision": [
            "DGA report",
            "Verify breaker position and trip circuit.",
        ],
    }

    details = build_explanation_provenance_details(hypothesis)

    lookup = {
        (item["field"], item["statement"]): item
        for item in details
    }

    support = lookup[
        (
            "why_supported",
            "Relay target supports differential operation.",
        )
    ]
    assert support["source_type"] == "supporting_evidence"
    assert support["source_path"] == "supporting_evidence[0]"
    assert support["traceable"] is True

    missing = lookup[
        (
            "confidence_limiters",
            "DGA report",
        )
    ]
    assert missing["source_type"] == "missing_evidence"
    assert missing["source_path"] == "missing_evidence[0]"
    assert missing["traceable"] is True

    conflict_description = lookup[
        (
            "why_not_confirmed",
            "Breaker failed to open after trip.",
        )
    ]
    assert (
        conflict_description["source_type"]
        == "conflict_description"
    )
    assert conflict_description["source_path"] == "conflicts[0]"
    assert conflict_description["traceable"] is True

    conflict_verification = lookup[
        (
            "evidence_that_would_change_decision",
            "Verify breaker position and trip circuit.",
        )
    ]
    assert (
        conflict_verification["source_type"]
        == "conflict_verification"
    )
    assert conflict_verification["source_path"] == "conflicts[0]"
    assert conflict_verification["traceable"] is True
