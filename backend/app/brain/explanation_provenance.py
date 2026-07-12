from __future__ import annotations

from typing import Any


EXPLANATION_FIELDS = (
    "why_supported",
    "why_not_confirmed",
    "confidence_drivers",
    "confidence_limiters",
    "evidence_that_would_change_decision",
)

STANDARD_FALLBACKS = {
    (
        "why_supported",
        "No direct supporting evidence is currently available.",
    ),
    (
        "why_not_confirmed",
        "No material confirmation limiter is currently identified.",
    ),
}


def build_explanation_provenance_details(
    hypothesis: dict[str, Any],
) -> list[dict[str, Any]]:
    supporting_evidence = hypothesis.get("supporting_evidence", [])
    missing_evidence = hypothesis.get("missing_evidence", [])
    conflicts = hypothesis.get("conflicts", [])

    if not isinstance(supporting_evidence, list):
        supporting_evidence = []

    if not isinstance(missing_evidence, list):
        missing_evidence = []

    if not isinstance(conflicts, list):
        conflicts = []

    details: list[dict[str, Any]] = []

    for field_name in EXPLANATION_FIELDS:
        statements = hypothesis.get(field_name, [])

        if not isinstance(statements, list):
            continue

        for statement_index, statement in enumerate(statements):
            source = _resolve_statement_source(
                field_name=field_name,
                statement=statement,
                supporting_evidence=supporting_evidence,
                missing_evidence=missing_evidence,
                conflicts=conflicts,
            )

            details.append({
                "field": field_name,
                "statement": statement,
                "statement_index": statement_index,
                **source,
            })

    return details


def _resolve_statement_source(
    field_name: str,
    statement: Any,
    supporting_evidence: list[Any],
    missing_evidence: list[Any],
    conflicts: list[Any],
) -> dict[str, Any]:
    if field_name in {"why_supported", "confidence_drivers"}:
        source_index = _find_item_index(
            supporting_evidence,
            statement,
        )

        if source_index is not None:
            return _traceable_source(
                source_type="supporting_evidence",
                source_field="supporting_evidence",
                source_index=source_index,
            )

    if field_name in {
        "why_not_confirmed",
        "confidence_limiters",
        "evidence_that_would_change_decision",
    }:
        source_index = _find_item_index(
            missing_evidence,
            statement,
        )

        if source_index is not None:
            return _traceable_source(
                source_type="missing_evidence",
                source_field="missing_evidence",
                source_index=source_index,
            )

    if field_name in {"why_not_confirmed", "confidence_limiters"}:
        conflict_index = _find_conflict_index(
            conflicts=conflicts,
            conflict_field="conflict",
            statement=statement,
        )

        if conflict_index is not None:
            return _traceable_source(
                source_type="conflict_description",
                source_field="conflicts",
                source_index=conflict_index,
            )

    if field_name == "evidence_that_would_change_decision":
        conflict_index = _find_conflict_index(
            conflicts=conflicts,
            conflict_field="recommended_verification",
            statement=statement,
        )

        if conflict_index is not None:
            return _traceable_source(
                source_type="conflict_verification",
                source_field="conflicts",
                source_index=conflict_index,
            )

    if (field_name, statement) in STANDARD_FALLBACKS:
        return {
            "source_type": "system_fallback",
            "source_field": None,
            "source_index": None,
            "source_path": None,
            "traceable": True,
        }

    return {
        "source_type": "unresolved",
        "source_field": None,
        "source_index": None,
        "source_path": None,
        "traceable": False,
    }


def _traceable_source(
    source_type: str,
    source_field: str,
    source_index: int,
) -> dict[str, Any]:
    return {
        "source_type": source_type,
        "source_field": source_field,
        "source_index": source_index,
        "source_path": f"{source_field}[{source_index}]",
        "traceable": True,
    }


def _find_item_index(
    items: list[Any],
    target: Any,
) -> int | None:
    for index, item in enumerate(items):
        if item == target:
            return index

    return None


def _find_conflict_index(
    conflicts: list[Any],
    conflict_field: str,
    statement: Any,
) -> int | None:
    for index, conflict in enumerate(conflicts):
        if not isinstance(conflict, dict):
            continue

        if conflict.get(conflict_field) == statement:
            return index

    return None


def summarize_explanation_provenance_integrity(
    details: list[dict[str, Any]],
) -> dict[str, Any]:
    """Summarize explanation traceability for audit use only.

    A None traceability ratio means there are no explanation
    statements to evaluate; it does not mean zero percent traceable.
    """
    if not isinstance(details, list):
        details = []

    total_statement_count = len(details)

    traceable_statement_count = sum(
        1
        for item in details
        if isinstance(item, dict)
        and item.get("traceable") is True
    )

    unresolved_statement_count = (
        total_statement_count - traceable_statement_count
    )

    if total_statement_count == 0:
        status = "not_applicable"
        traceability_ratio = None
    elif unresolved_statement_count == 0:
        status = "complete"
        traceability_ratio = 1.0
    else:
        status = "incomplete"
        traceability_ratio = round(
            traceable_statement_count / total_statement_count,
            2,
        )

    return {
        "status": status,
        "total_statement_count": total_statement_count,
        "traceable_statement_count": traceable_statement_count,
        "unresolved_statement_count": unresolved_statement_count,
        "traceability_ratio": traceability_ratio,
        "affects_decision": False,
    }
