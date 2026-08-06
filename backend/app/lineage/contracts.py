from __future__ import annotations

from enum import Enum
from typing import Any, Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


class FrozenLineageModel(BaseModel):
    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
    )


class LineageNodeType(str, Enum):
    SOURCE = "source"
    MEASUREMENT = "measurement"
    OBSERVATION = "observation"
    EVIDENCE = "evidence"
    HYPOTHESIS = "hypothesis"
    REASONING_STEP = "reasoning_step"
    SAFETY_GATE = "safety_gate"
    DECISION = "decision"


class LineageRelation(str, Enum):
    DERIVED_FROM = "derived_from"
    SUPPORTS = "supports"
    CONTRADICTS = "contradicts"
    VALIDATES = "validates"
    INVALIDATES = "invalidates"
    DEPENDS_ON = "depends_on"


class LineageReference(FrozenLineageModel):
    target_node_id: str = Field(
        min_length=1,
    )

    relation: LineageRelation

    rationale: str = Field(
        min_length=1,
    )

    source: str = Field(
        min_length=1,
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict,
    )

    shadow_only: Literal[True] = True
    affects_reasoning: Literal[False] = False
    affects_decision: Literal[False] = False


class LineageNode(FrozenLineageModel):
    node_id: str = Field(
        min_length=1,
    )

    node_type: LineageNodeType

    display_name: str = Field(
        min_length=1,
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict,
    )

    shadow_only: Literal[True] = True
    affects_reasoning: Literal[False] = False
    affects_decision: Literal[False] = False


class LineageEdge(FrozenLineageModel):
    source_node: str = Field(
        min_length=1,
    )

    target_node: str = Field(
        min_length=1,
    )

    relation: LineageRelation

    metadata: dict[str, Any] = Field(
        default_factory=dict,
    )

    shadow_only: Literal[True] = True
    affects_reasoning: Literal[False] = False
    affects_decision: Literal[False] = False


class LineageGraph(FrozenLineageModel):
    nodes: tuple[
        LineageNode,
        ...,
    ] = ()

    edges: tuple[
        LineageEdge,
        ...,
    ] = ()

    shadow_only: Literal[True] = True
    affects_reasoning: Literal[False] = False
    affects_decision: Literal[False] = False


class LineageAudit(FrozenLineageModel):
    node_count: int = Field(
        ge=0,
    )

    edge_count: int = Field(
        ge=0,
    )

    max_depth: int = Field(
        ge=0,
    )

    traceability_ratio: float = Field(
        ge=0.0,
        le=1.0,
    )

    complete: bool

    shadow_only: Literal[True] = True
    affects_reasoning: Literal[False] = False
    affects_decision: Literal[False] = False


class LineageValidation(FrozenLineageModel):
    valid: bool

    duplicate_node_ids: tuple[
        str,
        ...,
    ] = ()

    missing_source_nodes: tuple[
        str,
        ...,
    ] = ()

    missing_target_nodes: tuple[
        str,
        ...,
    ] = ()

    cycles: tuple[
        tuple[str, ...],
        ...,
    ] = ()

    orphan_nodes: tuple[
        str,
        ...,
    ] = ()

    shadow_only: Literal[True] = True
    affects_reasoning: Literal[False] = False
    affects_decision: Literal[False] = False