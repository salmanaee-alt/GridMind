from __future__ import annotations

from enum import Enum
from typing import Annotated

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)


NonBlankString = Annotated[
    str,
    Field(min_length=1),
]


class ProvenanceGapType(str, Enum):
    NONE = "none"
    NO_SUPPORTING_KNOWLEDGE = "no_supporting_knowledge"
    KNOWLEDGE_NOT_SELECTED = "knowledge_not_selected"
    INTERPRETATION_ONLY = "interpretation_only"
    UNKNOWN = "unknown"


class EvidenceConflictType(str, Enum):
    NONE = "none"

    SUPPORTING_VS_CONTRADICTING = (
        "supporting_vs_contradicting"
    )

    SENSOR_DISAGREEMENT = (
        "sensor_disagreement"
    )

    TIME_INCONSISTENCY = (
        "time_inconsistency"
    )

    MISSING_SUPPORT = (
        "missing_support"
    )

    UNKNOWN = "unknown"


class TraceableEvidenceItem(BaseModel):
    """
    One evidence interpretation with explicit traceability.

    This model is descriptive only.
    It does not determine hypothesis confidence,
    safety state, readiness, or engineering decisions.
    """

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
    )

    conflict_type: EvidenceConflictType = (
        EvidenceConflictType.NONE
    )
    
    evidence: NonBlankString
    interpretation: NonBlankString
    engineering_significance: NonBlankString

    supporting_knowledge_ids: tuple[
        NonBlankString,
        ...
    ] = ()

    provenance_gap: ProvenanceGapType = (
        ProvenanceGapType.NONE
    )

class TraceableEngineeringContextRequest(BaseModel):
    """
    Shadow-only input contract used to assemble
    traceable engineering context.
    """

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
    )

    domain: NonBlankString
    asset_type: NonBlankString
    investigation_stage: NonBlankString

    selected_knowledge_ids: tuple[
        NonBlankString,
        ...
    ] = ()

    evidence_items: tuple[
        TraceableEvidenceItem,
        ...
    ] = ()

    unresolved_evidence: tuple[
        NonBlankString,
        ...
    ] = ()

    @field_validator(
        "domain",
        "asset_type",
        "investigation_stage",
        mode="before",
    )
    @classmethod
    def normalize_required_string(
        cls,
        value: object,
    ) -> object:
        if isinstance(value, str):
            return value.strip()

        return value

    @field_validator(
        "selected_knowledge_ids",
        "unresolved_evidence",
        mode="before",
    )
    @classmethod
    def normalize_string_tuples(
        cls,
        value: object,
    ) -> object:
        if value is None:
            return ()

        if isinstance(value, (list, tuple)):
            return tuple(
                item.strip()
                if isinstance(item, str)
                else item
                for item in value
            )

        return value

    @model_validator(mode="after")
    def validate_traceability_input(
        self,
    ) -> "TraceableEngineeringContextRequest":
        if len(self.selected_knowledge_ids) != len(
            set(self.selected_knowledge_ids)
        ):
            raise ValueError(
                "selected_knowledge_ids must be unique."
            )

        interpreted_evidence = [
            item.evidence
            for item in self.evidence_items
        ]

        if len(interpreted_evidence) != len(
            set(interpreted_evidence)
        ):
            raise ValueError(
                "Evidence items must be unique."
            )

        if len(self.unresolved_evidence) != len(
            set(self.unresolved_evidence)
        ):
            raise ValueError(
                "unresolved_evidence must be unique."
            )

        overlap = set(
            interpreted_evidence
        ).intersection(
            self.unresolved_evidence
        )

        if overlap:
            raise ValueError(
                "Evidence cannot be both interpreted "
                "and unresolved."
            )

        selected_ids = set(
            self.selected_knowledge_ids
        )

        for item in self.evidence_items:
            unknown_ids = set(
                item.supporting_knowledge_ids
            ) - selected_ids

            if unknown_ids:
                raise ValueError(
                    "Evidence cannot reference knowledge "
                    "that was not selected."
                )

        return self


class TraceableEngineeringContextResult(BaseModel):
    """
    Auditable shadow context assembled from selected
    knowledge and interpreted evidence.
    """

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
    )

    knowledge_ids: tuple[
        NonBlankString,
        ...
    ] = ()

    evidence_items: tuple[
        TraceableEvidenceItem,
        ...
    ] = ()

    unresolved_evidence: tuple[
        NonBlankString,
        ...
    ] = ()

    traceability_complete: bool = False

    interpreted_evidence_count: int = Field(
        default=0,
        ge=0,
    )

    traced_evidence_count: int = Field(
        default=0,
        ge=0,
    )

    untraced_evidence_count: int = Field(
        default=0,
        ge=0,
    )

    traceability_ratio: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
    )

    untraced_evidence: tuple[
        NonBlankString,
        ...
    ] = ()

    affects_decision: bool = False
