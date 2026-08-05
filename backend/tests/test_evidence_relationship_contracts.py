import pytest
from pydantic import ValidationError

from app.brain.evidence_contracts import (
    EngineeringEvidence,
    EvidenceCategory,
    EvidenceRelationship,
    EvidenceRelationshipType,
)


def test_evidence_relationship_is_explicit():
    relationship = EvidenceRelationship(
        target_evidence_id="measurement:hv_current",
        relation=EvidenceRelationshipType.DERIVED_FROM,
        source="transformer_physics_adapter",
    )

    assert (
        relationship.target_evidence_id
        == "measurement:hv_current"
    )
    assert (
        relationship.relation
        == EvidenceRelationshipType.DERIVED_FROM
    )


def test_engineering_evidence_accepts_relationships():
    evidence = EngineeringEvidence(
        evidence_id="physics:differential_current",
        evidence_type="differential_current",
        category=EvidenceCategory.PHYSICS,
        source="transformer_physics",
        relationships=(
            EvidenceRelationship(
                target_evidence_id="measurement:hv_current",
                relation=(
                    EvidenceRelationshipType.DERIVED_FROM
                ),
                source="transformer_physics_adapter",
            ),
        ),
    )

    assert len(evidence.relationships) == 1
    assert (
        evidence.relationships[0].target_evidence_id
        == "measurement:hv_current"
    )
    assert evidence.affects_reasoning is False


def test_relationships_default_to_empty():
    evidence = EngineeringEvidence(
        evidence_id="physics:harmonic_restraint",
        evidence_type="harmonic_restraint",
        category=EvidenceCategory.PHYSICS,
        source="transformer_physics",
    )

    assert evidence.relationships == ()


def test_relationship_rejects_blank_target():
    with pytest.raises(ValidationError):
        EvidenceRelationship(
            target_evidence_id="",
            relation=EvidenceRelationshipType.SUPPORTS,
            source="test",
        )


def test_relationship_rejects_unknown_relation():
    with pytest.raises(ValidationError):
        EvidenceRelationship(
            target_evidence_id="evidence:target",
            relation="unknown_relation",
            source="test",
        )