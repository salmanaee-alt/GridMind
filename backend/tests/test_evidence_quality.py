import pytest

from app.transformer.evidence_quality import (
    score_evidence_quality,
)


def test_evidence_quality_deduplicates_available_evidence_names():
    result = score_evidence_quality(
        available_evidence=[
            "Relay event report",
            "Relay event report",
        ],
        missing_required_evidence=[],
    )

    assert result["completeness_score"] == 1.0
    assert result["directness_score"] == 1.0
    assert result["available_direct_evidence"] == [
        "Relay event report",
    ]


def test_evidence_quality_rejects_duplicate_metadata_names():
    duplicate_metadata = [
        {
            "evidence_name": "Relay event report",
            "source_type": "relay",
            "timestamp_relation": "during_event",
            "verified": True,
            "evidence_age_days": 1,
        },
        {
            "evidence_name": "Relay event report",
            "source_type": "relay",
            "timestamp_relation": "during_event",
            "verified": True,
            "evidence_age_days": 1,
        },
    ]

    with pytest.raises(
        ValueError,
        match="unique evidence_name",
    ):
        score_evidence_quality(
            available_evidence=[
                "Relay event report",
            ],
            missing_required_evidence=[],
            evidence_metadata=duplicate_metadata,
        )


def test_evidence_quality_does_not_mutate_input_lists():
    available = [
        "Relay event report",
        "Relay event report",
    ]
    missing = [
        "DGA report",
        "DGA report",
    ]

    available_before = list(available)
    missing_before = list(missing)

    score_evidence_quality(
        available_evidence=available,
        missing_required_evidence=missing,
    )

    assert available == available_before
    assert missing == missing_before


def test_evidence_quality_component_scores_are_bounded():
    result = score_evidence_quality(
        available_evidence=[
            "Relay event report",
            "Relay event report",
        ],
        missing_required_evidence=[
            "DGA report",
            "DGA report",
        ],
    )

    bounded_fields = [
        "quality_score",
        "completeness_score",
        "directness_score",
        "metadata_score",
        "verified_evidence_ratio",
        "source_reliability_score",
        "timestamp_relation_score",
        "freshness_score",
    ]

    for field in bounded_fields:
        assert 0.0 <= result[field] <= 1.0


def test_evidence_quality_deduplicates_missing_evidence_names():
    result = score_evidence_quality(
        available_evidence=[
            "Relay event report",
        ],
        missing_required_evidence=[
            "DGA report",
            "DGA report",
        ],
    )

    assert result["missing_required_evidence"] == [
        "DGA report",
    ]
