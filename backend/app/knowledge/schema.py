from __future__ import annotations

from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)


KnowledgeStatus = Literal[
    "draft",
    "reviewed",
    "approved",
    "deprecated",
]

EvidenceRole = Literal[
    "required",
    "supporting",
    "contradicting",
    "optional",
]

RelationshipType = Literal[
    "supports",
    "contradicts",
    "requires",
    "strengthens",
    "weakens",
    "causes",
    "caused_by",
    "verified_by",
    "invalidated_by",
    "related_to",
]

ReferenceType = Literal[
    "standard",
    "guide",
    "paper",
    "book",
    "oem_manual",
    "internal_standard",
    "field_record",
]


class FrozenKnowledgeModel(BaseModel):
    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        str_strip_whitespace=True,
    )


class EvidenceRequirement(FrozenKnowledgeModel):
    evidence_name: str = Field(min_length=1)
    evidence_role: EvidenceRole
    rationale: str = Field(min_length=1)


class EngineeringReference(FrozenKnowledgeModel):
    reference_type: ReferenceType
    organization: str = Field(min_length=1)
    document_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    clause: str | None = None


class EngineeringRelationship(FrozenKnowledgeModel):
    relationship_type: RelationshipType
    target_knowledge_id: str = Field(
        pattern=r"^[A-Z]{2,10}-EKO-[0-9]{4,}$"
    )
    description: str = Field(min_length=1)


class ValidationCase(FrozenKnowledgeModel):
    case_id: str = Field(min_length=1)
    description: str = Field(min_length=1)
    expected_outcome: str = Field(min_length=1)


class KnowledgeRevision(FrozenKnowledgeModel):
    version: str = Field(
        pattern=r"^[0-9]+\.[0-9]+\.[0-9]+$"
    )
    change_summary: str = Field(min_length=1)
    changed_by: str = Field(min_length=1)


class EngineeringKnowledgeObject(FrozenKnowledgeModel):
    knowledge_id: str = Field(
        pattern=r"^[A-Z]{2,10}-EKO-[0-9]{4,}$"
    )
    title: str = Field(min_length=1)
    domain: str = Field(min_length=1)
    category: str = Field(min_length=1)
    version: str = Field(
        pattern=r"^[0-9]+\.[0-9]+\.[0-9]+$"
    )
    status: KnowledgeStatus = "draft"

    definition: str = Field(min_length=1)
    physical_principles: tuple[str, ...] = ()

    evidence_requirements: tuple[
        EvidenceRequirement,
        ...,
    ] = ()

    relationships: tuple[
        EngineeringRelationship,
        ...,
    ] = ()

    references: tuple[
        EngineeringReference,
        ...,
    ] = ()

    validation_cases: tuple[
        ValidationCase,
        ...,
    ] = ()

    known_limitations: tuple[str, ...] = ()

    revision_history: tuple[
        KnowledgeRevision,
        ...,
    ] = ()

    @field_validator(
        "physical_principles",
        "known_limitations",
    )
    @classmethod
    def reject_blank_text_entries(
        cls,
        values: tuple[str, ...],
    ) -> tuple[str, ...]:
        if any(not value.strip() for value in values):
            raise ValueError(
                "knowledge text collections cannot contain "
                "blank entries."
            )

        return values

    @model_validator(mode="after")
    def validate_approved_knowledge(
        self,
    ) -> "EngineeringKnowledgeObject":
        if self.status == "approved":
            if not self.references:
                raise ValueError(
                    "approved knowledge requires at least "
                    "one engineering reference."
                )

            if not self.validation_cases:
                raise ValueError(
                    "approved knowledge requires at least "
                    "one validation case."
                )

            if not self.revision_history:
                raise ValueError(
                    "approved knowledge requires revision history."
                )

        return self
