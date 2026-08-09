from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from app.brain.evidence_graph_contracts import (
    EvidenceGraph,
)
from app.lineage.contracts import (
    LineageGraph,
)


class ThinkingGraphContext(BaseModel):
    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
    )

    evidence_graph: EvidenceGraph | None = None

    lineage_graph: LineageGraph | None = None

    shadow_only: bool = True

    affects_reasoning: bool = False

    affects_decision: bool = False