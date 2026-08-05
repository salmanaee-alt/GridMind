from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class EvidenceRelation(str, Enum):
    SUPPORTS = "supports"
    CONTRADICTS = "contradicts"
    DERIVED_FROM = "derived_from"
    DEPENDS_ON = "depends_on"
    VALIDATES = "validates"
    INVALIDATES = "invalidates"


class EvidenceNode(BaseModel):
    node_id: str
    evidence_id: str
    evidence_type: str
    category: str


class EvidenceEdge(BaseModel):
    source_node: str
    target_node: str
    relation: EvidenceRelation


class EvidenceGraph(BaseModel):
    nodes: list[EvidenceNode] = Field(default_factory=list)
    edges: list[EvidenceEdge] = Field(default_factory=list)

    shadow_only: bool = True
    affects_reasoning: bool = False
    affects_decision: bool = False
