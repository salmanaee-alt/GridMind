import pytest

from app.brain.engineering_brain import EngineeringBrain


def test_ranking_audit_matches_actual_hypothesis_order():
    hypotheses = [
        {
            "hypothesis": "Medium hypothesis",
            "confidence": "medium",
            "supporting_evidence": ["Evidence A"],
            "missing_evidence": [],
            "conflicts": [],
        },
        {
            "hypothesis": "High hypothesis",
            "confidence": "high",
            "supporting_evidence": [],
            "missing_evidence": ["Evidence B"],
            "conflicts": [],
        },
        {
            "hypothesis": "Supported medium hypothesis",
            "confidence": "medium",
            "supporting_evidence": [
                "Evidence C",
                "Evidence D",
            ],
            "missing_evidence": [],
            "conflicts": [],
        },
    ]

    brain = EngineeringBrain()
    ranked = brain._rank_hypotheses(hypotheses)

    brain._attach_hypothesis_ranking_audit(
        ranked_hypotheses=ranked,
        original_hypotheses=hypotheses,
    )

    assert [
        item["hypothesis"]
        for item in ranked
    ] == [
        "High hypothesis",
        "Supported medium hypothesis",
        "Medium hypothesis",
    ]

    high_audit = ranked[0]["ranking_audit"]

    assert high_audit == {
        "rank_position": 1,
        "original_position": 2,
        "confidence": "high",
        "confidence_rank": 3,
        "supporting_evidence_count": 0,
        "missing_evidence_count": 1,
        "conflict_count": 0,
        "ranking_key": [3, 0, -1, 0],
        "tie_breaker_policy": "stable_input_order",
        "ranking_algorithm": (
            "confidence_support_missing_conflict_v0.1"
        ),
        "affects_ranking": False,
        "ranking_algorithm_changed": False,
    }

    supported_medium_audit = ranked[1]["ranking_audit"]

    assert supported_medium_audit["rank_position"] == 2
    assert supported_medium_audit["original_position"] == 3
    assert supported_medium_audit["ranking_key"] == [
        2,
        2,
        0,
        0,
    ]


def test_ranking_audit_preserves_stable_order_for_equal_keys():
    hypotheses = [
        {
            "hypothesis": "First equal hypothesis",
            "confidence": "medium",
            "supporting_evidence": ["Evidence A"],
            "missing_evidence": [],
            "conflicts": [],
        },
        {
            "hypothesis": "Second equal hypothesis",
            "confidence": "medium",
            "supporting_evidence": ["Evidence B"],
            "missing_evidence": [],
            "conflicts": [],
        },
    ]

    brain = EngineeringBrain()
    ranked = brain._rank_hypotheses(hypotheses)

    order_before_audit = [
        item["hypothesis"]
        for item in ranked
    ]

    brain._attach_hypothesis_ranking_audit(
        ranked_hypotheses=ranked,
        original_hypotheses=hypotheses,
    )

    order_after_audit = [
        item["hypothesis"]
        for item in ranked
    ]

    assert order_before_audit == [
        "First equal hypothesis",
        "Second equal hypothesis",
    ]
    assert order_after_audit == order_before_audit

    first_audit = ranked[0]["ranking_audit"]
    second_audit = ranked[1]["ranking_audit"]

    assert first_audit["ranking_key"] == second_audit["ranking_key"]
    assert first_audit["original_position"] == 1
    assert second_audit["original_position"] == 2
    assert first_audit["tie_breaker_policy"] == "stable_input_order"
    assert second_audit["tie_breaker_policy"] == "stable_input_order"


def test_ranking_audit_does_not_modify_ranking_inputs():
    hypothesis = {
        "hypothesis": "Audit-only hypothesis",
        "confidence": "high",
        "supporting_evidence": ["Evidence A"],
        "missing_evidence": ["Evidence B"],
        "conflicts": [
            {
                "conflict": "Evidence conflict.",
                "severity": "medium",
            },
        ],
    }

    original_confidence = hypothesis["confidence"]
    original_supporting = list(hypothesis["supporting_evidence"])
    original_missing = list(hypothesis["missing_evidence"])
    original_conflicts = list(hypothesis["conflicts"])

    brain = EngineeringBrain()
    ranked = brain._rank_hypotheses([hypothesis])

    brain._attach_hypothesis_ranking_audit(
        ranked_hypotheses=ranked,
        original_hypotheses=[hypothesis],
    )

    assert hypothesis["confidence"] == original_confidence
    assert hypothesis["supporting_evidence"] == original_supporting
    assert hypothesis["missing_evidence"] == original_missing
    assert hypothesis["conflicts"] == original_conflicts
    assert hypothesis["ranking_audit"]["affects_ranking"] is False


def test_ranking_audit_rejects_duplicate_object_references():
    shared_hypothesis = {
        "hypothesis": "Repeated object",
        "confidence": "medium",
        "supporting_evidence": [],
        "missing_evidence": [],
        "conflicts": [],
    }

    hypotheses = [
        shared_hypothesis,
        shared_hypothesis,
    ]

    brain = EngineeringBrain()
    ranked = brain._rank_hypotheses(hypotheses)

    with pytest.raises(
        ValueError,
        match="unique hypothesis objects",
    ):
        brain._attach_hypothesis_ranking_audit(
            ranked_hypotheses=ranked,
            original_hypotheses=hypotheses,
        )


def test_ranking_audit_distinguishes_identical_content_objects():
    first = {
        "hypothesis": "Identical hypothesis",
        "confidence": "medium",
        "supporting_evidence": ["Evidence A"],
        "missing_evidence": [],
        "conflicts": [],
    }
    second = {
        "hypothesis": "Identical hypothesis",
        "confidence": "medium",
        "supporting_evidence": ["Evidence A"],
        "missing_evidence": [],
        "conflicts": [],
    }

    assert first == second
    assert first is not second

    hypotheses = [
        first,
        second,
    ]

    brain = EngineeringBrain()
    ranked = brain._rank_hypotheses(hypotheses)

    brain._attach_hypothesis_ranking_audit(
        ranked_hypotheses=ranked,
        original_hypotheses=hypotheses,
    )

    assert ranked[0] is first
    assert ranked[1] is second

    assert ranked[0]["ranking_audit"]["original_position"] == 1
    assert ranked[1]["ranking_audit"]["original_position"] == 2

    assert ranked[0]["ranking_audit"]["rank_position"] == 1
    assert ranked[1]["ranking_audit"]["rank_position"] == 2


def test_ranking_returns_new_list_without_reordering_input():
    hypotheses = [
        {
            "hypothesis": "Low hypothesis",
            "confidence": "low",
            "supporting_evidence": [],
            "missing_evidence": [],
            "conflicts": [],
        },
        {
            "hypothesis": "High hypothesis",
            "confidence": "high",
            "supporting_evidence": [],
            "missing_evidence": [],
            "conflicts": [],
        },
    ]

    original_order = [
        item["hypothesis"]
        for item in hypotheses
    ]

    ranked = EngineeringBrain()._rank_hypotheses(hypotheses)

    assert ranked is not hypotheses

    assert [
        item["hypothesis"]
        for item in hypotheses
    ] == original_order

    assert [
        item["hypothesis"]
        for item in ranked
    ] == [
        "High hypothesis",
        "Low hypothesis",
    ]
