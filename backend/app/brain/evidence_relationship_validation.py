from __future__ import annotations

from pydantic import BaseModel, Field

from app.brain.evidence_contracts import (
    EngineeringEvidence,
)


class EvidenceRelationshipValidationResult(BaseModel):
    valid: bool

    missing_targets: list[str] = Field(
        default_factory=list
    )

    self_references: list[str] = Field(
        default_factory=list
    )

    duplicate_relationships: list[str] = Field(
        default_factory=list
    )

    affects_reasoning: bool = False
    affects_decision: bool = False


def validate_evidence_relationships(
    evidence_items: list[EngineeringEvidence],
) -> EvidenceRelationshipValidationResult:
    known_evidence_ids = {
        item.evidence_id
        for item in evidence_items
    }

    missing_targets: set[str] = set()
    self_references: set[str] = set()
    duplicate_relationships: set[str] = set()

    seen_relationships: set[
        tuple[str, str, str]
    ] = set()

    for item in evidence_items:
        for relationship in item.relationships:
            key = (
                item.evidence_id,
                relationship.target_evidence_id,
                relationship.relation.value,
            )

            if key in seen_relationships:
                duplicate_relationships.add(
                    "|".join(key)
                )
            else:
                seen_relationships.add(key)

            if (
                relationship.target_evidence_id
                not in known_evidence_ids
            ):
                missing_targets.add(
                    relationship.target_evidence_id
                )

            if (
                relationship.target_evidence_id
                == item.evidence_id
            ):
                self_references.add(
                    item.evidence_id
                )

    valid = not any([
        missing_targets,
        self_references,
        duplicate_relationships,
    ])

    return EvidenceRelationshipValidationResult(
        valid=valid,
        missing_targets=sorted(missing_targets),
        self_references=sorted(self_references),
        duplicate_relationships=sorted(
            duplicate_relationships
        ),
        affects_reasoning=False,
        affects_decision=False,
    )
