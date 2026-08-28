from copy import deepcopy

from app.reasoning.shadow_hypothesis_enrichment import (
    enrich_hypothesis_with_shadow_support,
)


def test_shadow_enrichment_adds_support_without_changing_decision_fields():
    hypothesis = {
        "hypothesis": "External fault with CT saturation",
        "confidence": "low",
        "supporting_evidence": [],
        "missing_evidence": [
            "Through-fault records",
        ],
        "conflicts": [],
        "why_supported": [],
        "confidence_drivers": [],
        "recommended_next_action": (
            "Review through-fault records."
        ),
    }

    original = deepcopy(hypothesis)

    enriched = enrich_hypothesis_with_shadow_support(
        hypothesis=hypothesis,
        support=(
            "Physics discrimination supports an external "
            "fault with CT saturation scenario."
        ),
        source="physics:external_fault_discrimination",
    )

    assert (
        "Physics discrimination supports an external "
        "fault with CT saturation scenario."
        in enriched["supporting_evidence"]
    )

    assert enriched["confidence"] == original["confidence"]
    assert (
        enriched["missing_evidence"]
        == original["missing_evidence"]
    )
    assert enriched["conflicts"] == original["conflicts"]
    assert (
        enriched["recommended_next_action"]
        == original["recommended_next_action"]
    )

    assert hypothesis == original


def test_shadow_enrichment_preserves_protected_fields():
    hypothesis = {
        "hypothesis": "External fault with CT saturation",
        "confidence": "low",
        "ranking": 4,
        "risk": "medium",
        "readiness": "not_ready",
        "safety": "review_required",
        "decision": "do_not_reenergize",
        "supporting_evidence": [],
        "missing_evidence": [
            "Through-fault records",
        ],
        "conflicts": [
            {
                "conflict": "Unverified protection sequence",
                "severity": "medium",
            }
        ],
        "recommended_next_action": (
            "Review through-fault records."
        ),
    }

    original = deepcopy(hypothesis)

    enriched = enrich_hypothesis_with_shadow_support(
        hypothesis=hypothesis,
        support=(
            "Physics discrimination supports an external "
            "fault with CT saturation scenario."
        ),
        source="physics:external_fault_discrimination",
    )

    protected_fields = (
        "confidence",
        "ranking",
        "risk",
        "readiness",
        "safety",
        "decision",
        "missing_evidence",
        "conflicts",
        "recommended_next_action",
    )

    for field in protected_fields:
        assert enriched[field] == original[field]

    assert hypothesis == original


def test_shadow_enrichment_does_not_duplicate_support():
    support = (
        "Physics discrimination supports an external "
        "fault with CT saturation scenario."
    )

    hypothesis = {
        "hypothesis": "External fault with CT saturation",
        "confidence": "low",
        "supporting_evidence": [support],
    }

    enriched = enrich_hypothesis_with_shadow_support(
        hypothesis=hypothesis,
        support=support,
        source="physics:external_fault_discrimination",
    )

    assert enriched["supporting_evidence"] == [
        support
    ]


def test_shadow_enrichment_can_be_limited_to_target_hypothesis():
    hypothesis = {
        "hypothesis": "Internal transformer fault",
        "confidence": "medium",
        "supporting_evidence": [],
    }

    original = deepcopy(hypothesis)

    if (
        hypothesis["hypothesis"]
        == "External fault with CT saturation"
    ):
        enriched = enrich_hypothesis_with_shadow_support(
            hypothesis=hypothesis,
            support=(
                "Physics discrimination supports an external "
                "fault with CT saturation scenario."
            ),
            source=(
                "physics:external_fault_discrimination"
            ),
        )
    else:
        enriched = deepcopy(hypothesis)

    assert enriched == original


def test_shadow_enrichment_applies_only_to_target_hypothesis():
    hypothesis = {
        "hypothesis": "External fault with CT saturation",
        "confidence": "low",
        "supporting_evidence": [],
    }

    enriched = enrich_hypothesis_with_shadow_support(
        hypothesis=hypothesis,
        target_hypothesis=(
            "External fault with CT saturation"
        ),
        support=(
            "Physics discrimination supports an external "
            "fault with CT saturation scenario."
        ),
        source="physics:external_fault_discrimination",
    )

    assert len(enriched["supporting_evidence"]) == 1


def test_shadow_enrichment_skips_non_target_hypothesis():
    hypothesis = {
        "hypothesis": "Internal transformer fault",
        "confidence": "medium",
        "supporting_evidence": [],
    }

    original = deepcopy(hypothesis)

    enriched = enrich_hypothesis_with_shadow_support(
        hypothesis=hypothesis,
        target_hypothesis=(
            "External fault with CT saturation"
        ),
        support=(
            "Physics discrimination supports an external "
            "fault with CT saturation scenario."
        ),
        source="physics:external_fault_discrimination",
    )

    assert enriched == original
    assert hypothesis == original


def test_shadow_enrichment_records_support_source():
    hypothesis = {
        "hypothesis": "External fault with CT saturation",
        "confidence": "low",
        "supporting_evidence": [],
    }

    enriched = enrich_hypothesis_with_shadow_support(
        hypothesis=hypothesis,
        target_hypothesis=(
            "External fault with CT saturation"
        ),
        support=(
            "Physics discrimination supports an external "
            "fault with CT saturation scenario."
        ),
        source="physics:external_fault_discrimination",
    )

    provenance = enriched[
        "shadow_support_provenance"
    ]

    assert provenance == [
        {
            "support": (
                "Physics discrimination supports an external "
                "fault with CT saturation scenario."
            ),
            "source": (
                "physics:external_fault_discrimination"
            ),
        }
    ]


def test_shadow_enrichment_does_not_duplicate_provenance():
    support = (
        "Physics discrimination supports an external "
        "fault with CT saturation scenario."
    )

    hypothesis = {
        "hypothesis": "External fault with CT saturation",
        "confidence": "low",
        "supporting_evidence": [support],
        "shadow_support_provenance": [
            {
                "support": support,
                "source": (
                    "physics:external_fault_discrimination"
                ),
            }
        ],
    }

    enriched = enrich_hypothesis_with_shadow_support(
        hypothesis=hypothesis,
        target_hypothesis=(
            "External fault with CT saturation"
        ),
        support=support,
        source="physics:external_fault_discrimination",
    )

    assert len(
        enriched["shadow_support_provenance"]
    ) == 1


def test_shadow_enrichment_does_not_add_provenance_to_non_target():
    hypothesis = {
        "hypothesis": "Internal transformer fault",
        "confidence": "medium",
        "supporting_evidence": [],
    }

    original = deepcopy(hypothesis)

    enriched = enrich_hypothesis_with_shadow_support(
        hypothesis=hypothesis,
        target_hypothesis=(
            "External fault with CT saturation"
        ),
        support=(
            "Physics discrimination supports an external "
            "fault with CT saturation scenario."
        ),
        source=(
            "physics:external_fault_discrimination"
        ),
    )

    assert enriched == original
    assert "shadow_support_provenance" not in enriched
    assert hypothesis == original