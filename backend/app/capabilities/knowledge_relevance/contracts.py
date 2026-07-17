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


class KnowledgeRelevanceRequest(BaseModel):
    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
    )

    domain: NonBlankString
    asset_type: NonBlankString
    available_evidence: tuple[NonBlankString, ...] = ()
    missing_evidence: tuple[NonBlankString, ...] = ()
    investigation_stage: NonBlankString
    max_results: int = Field(gt=0)

    @field_validator(
        "domain",
        "asset_type",
        "investigation_stage",
        mode="before",
    )
    @classmethod
    def normalize_required_string(cls, value: object) -> object:
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


class KnowledgeRelevanceResult(BaseModel):
    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
    )

    selected_ids: tuple[NonBlankString, ...] = ()
    scores: tuple[float, ...] = ()
    selection_reasons: tuple[NonBlankString, ...] = ()
    ignored_ids: tuple[NonBlankString, ...] = ()

    @field_validator("scores")
    @classmethod
    def validate_scores(
        cls,
        value: tuple[float, ...],
    ) -> tuple[float, ...]:
        if any(score < 0.0 or score > 1.0 for score in value):
            raise ValueError(
                "Scores must be between 0.0 and 1.0."
            )

        if tuple(value) != tuple(
            sorted(value, reverse=True)
        ):
            raise ValueError(
                "Scores must be sorted descending."
            )

        return value

    @model_validator(mode="after")
    def validate_output_integrity(
        self,
    ) -> "KnowledgeRelevanceResult":
        expected_length = len(self.selected_ids)

        if len(self.scores) != expected_length:
            raise ValueError(
                "selected_ids and scores must have equal lengths."
            )

        if len(self.selection_reasons) != expected_length:
            raise ValueError(
                "selected_ids and selection_reasons "
                "must have equal lengths."
            )

        if len(set(self.selected_ids)) != expected_length:
            raise ValueError(
                "selected_ids must be unique."
            )

        if len(set(self.ignored_ids)) != len(self.ignored_ids):
            raise ValueError(
                "ignored_ids must be unique."
            )

        overlap = set(self.selected_ids).intersection(
            self.ignored_ids
        )

        if overlap:
            raise ValueError(
                "Selected IDs cannot also be ignored."
            )

        return self
