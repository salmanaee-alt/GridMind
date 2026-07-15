from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import (
    Field,
    field_validator,
    model_validator,
)

from app.capabilities.contracts import (
    FrozenCapabilityModel,
)


class CandidateSource(str, Enum):
    REGISTRY = "registry"


class CandidateReason(FrozenCapabilityModel):
    code: str = Field(
        pattern=r"^[a-z][a-z0-9_]{1,63}$"
    )
    description: str = Field(
        min_length=1,
        max_length=1000,
    )

    @field_validator("description")
    @classmethod
    def validate_description(
        cls,
        value: str,
    ) -> str:
        normalized = value.strip()

        if not normalized:
            raise ValueError(
                "Candidate reason description must not be blank."
            )

        return normalized


class KnowledgeCandidate(FrozenCapabilityModel):
    knowledge_id: str = Field(
        pattern=r"^[A-Z]{2,10}-EKO-[0-9]{4,}$"
    )
    source: CandidateSource
    reason: CandidateReason
    shadow_only: Literal[True] = True
    affects_decision: Literal[False] = False


class KnowledgeCandidateResult(FrozenCapabilityModel):
    candidates: tuple[
        KnowledgeCandidate,
        ...,
    ] = ()
    candidate_count: int = Field(
        ge=0,
    )
    shadow_only: Literal[True] = True
    affects_decision: Literal[False] = False

    @model_validator(mode="after")
    def validate_candidate_count(
        self,
    ) -> "KnowledgeCandidateResult":
        if self.candidate_count != len(self.candidates):
            raise ValueError(
                "candidate_count must match the number of "
                "candidates."
            )

        return self
