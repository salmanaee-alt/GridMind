from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


class FrozenGraphModel(BaseModel):
    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
    )


class GraphDirection(str, Enum):
    DIRECTED = "directed"
    UNDIRECTED = "undirected"


class GraphNode(FrozenGraphModel):
    node_id: str = Field(
        min_length=1,
    )

    node_type: str = Field(
        min_length=1,
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict,
    )


class GraphEdge(FrozenGraphModel):
    source_node_id: str = Field(
        min_length=1,
    )

    target_node_id: str = Field(
        min_length=1,
    )

    relation: str = Field(
        min_length=1,
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict,
    )


class EngineeringGraph(FrozenGraphModel):
    graph_id: str = Field(
        min_length=1,
    )

    direction: GraphDirection = (
        GraphDirection.DIRECTED
    )

    nodes: tuple[
        GraphNode,
        ...,
    ] = ()

    edges: tuple[
        GraphEdge,
        ...,
    ] = ()

    metadata: dict[str, Any] = Field(
        default_factory=dict,
    )