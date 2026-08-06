from __future__ import annotations

from app.lineage.contracts import (
    LineageGraph,
    LineageValidation,
)
from app.lineage.graph_utils import (
    find_cycles,
)


def validate_lineage_graph(
    graph: LineageGraph,
) -> LineageValidation:
    node_ids = {
        node.node_id
        for node in graph.nodes
    }

    duplicate_node_ids: list[str] = []
    seen_node_ids: set[str] = set()

    for node in graph.nodes:
        if node.node_id in seen_node_ids:
            duplicate_node_ids.append(
                node.node_id
            )
        else:
            seen_node_ids.add(node.node_id)

    missing_sources: list[str] = []
    missing_targets: list[str] = []

    for edge in graph.edges:
        if edge.source_node not in node_ids:
            missing_sources.append(
                edge.source_node
            )

        if edge.target_node not in node_ids:
            missing_targets.append(
                edge.target_node
            )

    cycles = find_cycles(graph)

    return LineageValidation(
        valid=(
            not duplicate_node_ids
            and not missing_sources
            and not missing_targets
            and not cycles
        ),
        duplicate_node_ids=tuple(
            sorted(set(duplicate_node_ids))
        ),
        missing_source_nodes=tuple(
            sorted(set(missing_sources))
        ),
        missing_target_nodes=tuple(
            sorted(set(missing_targets))
        ),
        cycles=cycles,
        orphan_nodes=(),
    )