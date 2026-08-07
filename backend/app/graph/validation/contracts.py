from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class GraphValidation(BaseModel):
    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
    )

    valid: bool

    duplicate_node_ids: tuple[str, ...] = ()

    duplicate_edges: tuple[str, ...] = ()

    missing_source_nodes: tuple[str, ...] = ()

    missing_target_nodes: tuple[str, ...] = ()

    orphan_nodes: tuple[str, ...] = ()

    cycles: tuple[
        tuple[str, ...],
        ...
    ] = ()

    affects_reasoning: bool = False

    affects_decision: bool = False