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


class EvidenceInterpretationRequest(BaseModel):
    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
    )

    domain: NonBlankString
    asset_type: NonBlankString
    available_evidence: tuple[NonBlankString, ...] = ()
    missing_evidence: tuple[NonBlankString, ...] = ()
    investigation_stage: NonBlankString

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
            value = value.strip()

        return value

    @field_validator(
        "available_evidence",
        "missing_evidence",
        mode="before",
    )
    @classmethod
    def normalize_evidence(
        cls,
        value: object,
    ) -> object:
        if value is None:
            return ()

        if isinstance(value, (list, tuple)):
            normalized = []

            for item in value:
                if isinstance(item, str):
                    item = item.strip()

                normalized.append(item)

            return tuple(normalized)

        return value

    @field_validator(
        "available_evidence",
        "missing_evidence",
    )
    @classmethod
    def reject_duplicate_evidence(
        cls,
        value: tuple[str, ...],
    ) -> tuple[str, ...]:
        if len(value) != len(set(value)):
            raise ValueError(
                "Evidence entries must be unique."
            )

        return value

    @model_validator(mode="after")
    def reject_evidence_overlap(
        self,
    ) -> "EvidenceInterpretationRequest":
        overlap = set(
            self.available_evidence
        ).intersection(
            self.missing_evidence
        )

        if overlap:
            raise ValueError(
                "Evidence cannot be both available "
                "and missing."
            )

        return self


class EvidenceInterpretationItem(BaseModel):
    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
    )

    evidence: NonBlankString
    interpretation: NonBlankString
    engineering_significance: NonBlankString


class EvidenceInterpretationResult(BaseModel):
    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
    )

    interpretations: tuple[
        EvidenceInterpretationItem,
        ...
    ] = ()

    unresolved_evidence: tuple[
        NonBlankString,
        ...
    ] = ()

    @model_validator(mode="after")
    def validate_output_integrity(
        self,
    ) -> "EvidenceInterpretationResult":
        interpreted_evidence = [
            item.evidence
            for item in self.interpretations
        ]

        if len(interpreted_evidence) != len(
            set(interpreted_evidence)
        ):
            raise ValueError(
                "Interpreted evidence must be unique."
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

        return self
    