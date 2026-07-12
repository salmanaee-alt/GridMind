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
