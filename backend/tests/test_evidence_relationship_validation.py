from app.brain.evidence_contracts import (
    EngineeringEvidence,
    EvidenceCategory,
    EvidenceRelationship,
    EvidenceRelationshipType,
)
from app.brain.evidence_relationship_validation import (
    validate_evidence_relationships,
)


def _evidence(
    evidence_id: str,
    relationships=(),
) -> EngineeringEvidence:
    return EngineeringEvidence(
        evidence_id=evidence_id,
        evidence_type="test",
        category=EvidenceCategory.PHYSICS,
        source="test",
        relationships=relationships,
    )


def test_relationship_validation_accepts_valid_relationships():
    source = _evidence(
        "e1",
        relationships=(
            EvidenceRelationship(
                target_evidence_id="e2",
                relation=(
                    EvidenceRelationshipType.DERIVED_FROM
                ),
                source="test",
                rationale=(
                    "The differential current is derived from the "
                    "high-voltage current measurement."
                ),
            ),
        ),
    )

    target = _evidence("e2")

    result = validate_evidence_relationships(
        [source, target]
    )

    assert result.valid is True
    assert result.missing_targets == []
    assert result.self_references == []
    assert result.duplicate_relationships == []
    assert result.affects_reasoning is False
    assert result.affects_decision is False


def test_detects_missing_target():
    source = _evidence(
        "e1",
        relationships=(
            EvidenceRelationship(
                target_evidence_id="missing",
                relation=(
                    EvidenceRelationshipType.SUPPORTS
                ),
                source="test",
                rationale=(
                    "Differential current is explicitly derived "
                    "from the referenced measurement evidence."
                ),
            ),
        ),
    )

    result = validate_evidence_relationships([source])

    assert result.valid is False
    assert result.missing_targets == ["missing"]


def test_detects_self_reference():
    source = _evidence(
        "e1",
        relationships=(
            EvidenceRelationship(
                target_evidence_id="e1",
                relation=(
                    EvidenceRelationshipType.DEPENDS_ON
                ),
                source="test",
                rationale=(
                    "Differential current is explicitly derived "
                    "from the referenced measurement evidence."
                ),
            ),
        ),
    )

    result = validate_evidence_relationships([source])

    assert result.valid is False
    assert result.self_references == ["e1"]


def test_detects_duplicate_relationship():
    relationship = EvidenceRelationship(
        target_evidence_id="e2",
        relation=EvidenceRelationshipType.VALIDATES,
        source="test",
        rationale=(
            "Differential current is explicitly derived "
            "from the referenced measurement evidence."
        ),
    )

    source = _evidence(
        "e1",
        relationships=(
            relationship,
            relationship,
        ),
    )

    target = _evidence("e2")

    result = validate_evidence_relationships(
        [source, target]
    )

    assert result.valid is False
    assert result.duplicate_relationships == [
        "e1|e2|validates"
    ]


def test_reports_all_relationship_failures_together():
    duplicate = EvidenceRelationship(
        target_evidence_id="missing",
        relation=EvidenceRelationshipType.INVALIDATES,
        source="test",
        rationale=(
            "Differential current is explicitly derived "
            "from the referenced measurement evidence."
        ),
    )

    source = _evidence(
        "e1",
        relationships=(
            duplicate,
            duplicate,
            EvidenceRelationship(
                target_evidence_id="e1",
                relation=(
                    EvidenceRelationshipType.DEPENDS_ON
                ),
                source="test",
                rationale=(
                    "Differential current is explicitly derived "
                    "from the referenced measurement evidence."
                ),
            ),
        ),
    )

    result = validate_evidence_relationships([source])

    assert result.valid is False
    assert result.missing_targets == ["missing"]
    assert result.self_references == ["e1"]
    assert result.duplicate_relationships == [
        "e1|missing|invalidates"
    ]