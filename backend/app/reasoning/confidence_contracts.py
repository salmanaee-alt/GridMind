from __future__ import annotations

from typing import Any

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)

from app.graph.contracts import (
    EngineeringGraph,
)


class FrozenConfidenceModel(BaseModel):
    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
    )


class ConfidenceEdgeWeight(
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

    weight: float = Field(
        ge=0.0,
        le=1.0,
    )

    @field_validator(
        "weight",
        mode="before",
    )
    @classmethod
    def reject_boolean_weight(
        cls,
        value: Any,
    ) -> Any:
        if isinstance(
            value,
            bool,
        ):
            raise ValueError(
                "edge weight must not be boolean."
            )

        return value


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

    edge_weights: tuple[
        ConfidenceEdgeWeight,
        ...
    ] = ()

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

    @model_validator(mode="after")
    def reject_duplicate_edge_weights(
        self,
    ) -> "ConfidencePropagationRequest":
        identities = [
            (
                item.source_node,
                item.target_node,
                item.relation,
            )
            for item in self.edge_weights
        ]

        if len(identities) != len(set(identities)):
            raise ValueError(
                "edge weights must be unique by "
                "source, target, and relation."
            )

        return self

    @model_validator(mode="after")
    def validate_edge_weight_targets(
        self,
    ) -> "ConfidencePropagationRequest":
        graph_edges = {
            (
                edge.source_node_id,
                edge.target_node_id,
                edge.relation,
            )
            for edge in self.graph.edges
        }

        for item in self.edge_weights:
            identity = (
                item.source_node,
                item.target_node,
                item.relation,
            )

            if identity not in graph_edges:
                raise ValueError(
                    "edge weight must reference an "
                    "existing graph edge with matching "
                    "source, target, and relation."
                )

        return self


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
        ...
    ] = ()
    