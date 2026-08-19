from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from typing import Any

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)

from app.graph.contracts import (
    EngineeringGraph,
)

class FrozenConfidenceModel(BaseModel):
    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
    )


class ConfidencePropagationRequest(
    FrozenConfidenceModel,
):
    graph: EngineeringGraph

    confidence_scores: dict[
        str,
        float,
    ] = Field(
        default_factory=dict,
    )

    @field_validator(
        "confidence_scores",
        mode="before",
    )
    @classmethod
    def validate_confidence_scores(
        cls,
        value: Any,
    ) -> Any:
        if not isinstance(
            value,
            dict,
        ):
            return value

        validated: dict[
            str,
            float,
        ] = {}

        for node_id, confidence in value.items():
            if (
                not isinstance(
                    node_id,
                    str,
                )
                or not node_id
            ):
                raise ValueError(
                    "confidence score keys must be "
                    "non-empty strings."
                )

            if (
                not isinstance(
                    confidence,
                    (int, float),
                )
                or isinstance(
                    confidence,
                    bool,
                )
            ):
                raise ValueError(
                    "confidence scores must be numeric "
                    "and must not be booleans."
                )

            confidence = float(
                confidence
            )

            if (
                confidence < -1.0
                or confidence > 1.0
            ):
                raise ValueError(
                    "confidence scores must be within "
                    "[-1.0, 1.0]."
                )

            validated[
                node_id
            ] = confidence

        return validated


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