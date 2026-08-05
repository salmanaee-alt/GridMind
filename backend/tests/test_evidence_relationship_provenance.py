import pytest
from pydantic import ValidationError

from app.brain.evidence_contracts import (
    EvidenceRelationship,
    EvidenceRelationshipType,
)


def test_relationship_requires_rationale():
    with pytest.raises(ValidationError):
        EvidenceRelationship(
            target_evidence_id="measurement:hv_current",
            relation=(
                EvidenceRelationshipType.DERIVED_FROM
            ),
            source="transformer_physics_adapter",
        )


def test_relationship_accepts_explicit_provenance():
    relationship = EvidenceRelationship(
        target_evidence_id="measurement:hv_current",
        relation=(
            EvidenceRelationshipType.DERIVED_FROM
        ),
        source="transformer_physics_adapter",
        rationale=(
            "Differential current is explicitly derived "
            "from the HV current measurement."
        ),
        rule_id="transformer.physics.derived_from",
        rule_version="v0.43",
        derivation_type="adapter",
    )

    assert relationship.rationale
    assert (
        relationship.rule_id
        == "transformer.physics.derived_from"
    )
    assert relationship.rule_version == "v0.43"
    assert relationship.derivation_type == "adapter"
    assert relationship.affects_reasoning is False
    assert relationship.affects_decision is False


def test_relationship_allows_no_rule_reference():
    relationship = EvidenceRelationship(
        target_evidence_id="measurement:hv_current",
        relation=EvidenceRelationshipType.DEPENDS_ON,
        source="manual_engineering_input",
        rationale=(
            "The relationship was explicitly entered "
            "by an engineering reviewer."
        ),
    )

    assert relationship.rule_id is None
    assert relationship.rule_version is None
    assert relationship.derivation_type == "explicit"


def test_relationship_rejects_blank_rationale():
    with pytest.raises(ValidationError):
        EvidenceRelationship(
            target_evidence_id="measurement:hv_current",
            relation=EvidenceRelationshipType.SUPPORTS,
            source="engineering_rule",
            rationale="",
        )