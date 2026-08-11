from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class FrozenConfidenceModel(BaseModel):
    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
    )


class ConfidenceContribution(
    FrozenConfidenceModel,
):
    source_node: str = Field(
        min_length=1,
    )

    target_node: str = Field(
        min_length=1,
    )

    relation: str = Field(
        min_length=1,
    )

    incoming_confidence: float = Field(
        ge=-1.0,
        le=1.0,
    )

    edge_weight: float

    attenuation: float = Field(
        ge=0.0,
        le=1.0,
    )

    propagated_confidence: float


class ConfidencePropagationResult(
    FrozenConfidenceModel,
):
    propagated_scores: dict[
        str,
        float,
    ] = Field(
        default_factory=dict,
    )

    contributions: tuple[
        ConfidenceContribution,
        ...,
    ] = ()