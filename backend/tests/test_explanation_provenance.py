from app.brain.engineering_brain import EngineeringBrain
from app.brain.explanation_provenance import (
    build_explanation_provenance_details,
    summarize_explanation_provenance_integrity,
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


def test_explanation_provenance_handles_malformed_source_fields():
    hypothesis = {
        "supporting_evidence": None,
        "missing_evidence": "DGA report",
        "conflicts": {
            "conflict": "Malformed conflict container.",
        },
        "why_supported": [
            "Statement without a valid source container.",
        ],
        "why_not_confirmed": [],
        "confidence_drivers": [],
        "confidence_limiters": [],
        "evidence_that_would_change_decision": [],
    }

    details = build_explanation_provenance_details(hypothesis)

    assert len(details) == 1
    assert details[0]["source_type"] == "unresolved"
    assert details[0]["traceable"] is False
    assert details[0]["source_path"] is None


def test_explanation_provenance_marks_untraceable_statement_unresolved():
    hypothesis = {
        "supporting_evidence": [],
        "missing_evidence": [],
        "conflicts": [],
        "why_supported": [
            "Analyst note without an engineering source.",
        ],
        "why_not_confirmed": [],
        "confidence_drivers": [],
        "confidence_limiters": [],
        "evidence_that_would_change_decision": [],
    }

    details = build_explanation_provenance_details(hypothesis)

    unresolved = details[0]

    assert unresolved["field"] == "why_supported"
    assert unresolved["statement_index"] == 0
    assert unresolved["source_type"] == "unresolved"
    assert unresolved["source_field"] is None
    assert unresolved["source_index"] is None
    assert unresolved["source_path"] is None
    assert unresolved["traceable"] is False


def test_duplicate_statement_across_fields_has_independent_audit_records():
    statement = "Relay target supports differential operation."

    hypothesis = {
        "supporting_evidence": [
            statement,
        ],
        "missing_evidence": [],
        "conflicts": [],
        "why_supported": [
            statement,
        ],
        "why_not_confirmed": [],
        "confidence_drivers": [
            statement,
        ],
        "confidence_limiters": [],
        "evidence_that_would_change_decision": [],
    }

    details = build_explanation_provenance_details(hypothesis)

    matching = [
        item
        for item in details
        if item["statement"] == statement
    ]

    assert len(matching) == 2
    assert {
        item["field"]
        for item in matching
    } == {
        "why_supported",
        "confidence_drivers",
    }

    assert all(
        item["statement_index"] == 0
        for item in matching
    )
    assert all(
        item["source_type"] == "supporting_evidence"
        for item in matching
    )
    assert all(
        item["source_path"] == "supporting_evidence[0]"
        for item in matching
    )
    assert all(
        item["traceable"] is True
        for item in matching
    )


def test_provenance_integrity_summary_reports_incomplete():
    details = [
        {
            "source_type": "supporting_evidence",
            "traceable": True,
        },
        {
            "source_type": "unresolved",
            "traceable": False,
        },
    ]

    summary = summarize_explanation_provenance_integrity(
        details
    )

    assert summary == {
        "status": "incomplete",
        "total_statement_count": 2,
        "traceable_statement_count": 1,
        "unresolved_statement_count": 1,
        "traceability_ratio": 0.5,
        "affects_decision": False,
    }


def test_provenance_integrity_summary_reports_not_applicable():
    summary = summarize_explanation_provenance_integrity([])

    assert summary == {
        "status": "not_applicable",
        "total_statement_count": 0,
        "traceable_statement_count": 0,
        "unresolved_statement_count": 0,
        "traceability_ratio": None,
        "affects_decision": False,
    }


def test_engineering_brain_attaches_provenance_integrity():
    statement = "Relay target supports operation."

    hypothesis = {
        "supporting_evidence": [
            statement,
        ],
        "missing_evidence": [],
        "conflicts": [],
        "why_supported": [
            statement,
        ],
        "why_not_confirmed": [],
        "confidence_drivers": [
            statement,
        ],
        "confidence_limiters": [],
        "evidence_that_would_change_decision": [],
    }

    EngineeringBrain()._attach_explanation_provenance(
        [hypothesis]
    )

    assert len(
        hypothesis["explanation_provenance_details"]
    ) == 2

    assert hypothesis[
        "explanation_provenance_integrity"
    ] == {
        "status": "complete",
        "total_statement_count": 2,
        "traceable_statement_count": 2,
        "unresolved_statement_count": 0,
        "traceability_ratio": 1.0,
        "affects_decision": False,
    }
