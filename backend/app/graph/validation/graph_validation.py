from __future__ import annotations

from app.graph.algorithms.cycles import (
    find_cycles,
)
from app.graph.contracts import (
    EngineeringGraph,
)
from app.graph.validation.contracts import (
    GraphValidation,
)


def validate_graph(
    graph: EngineeringGraph,
) -> GraphValidation:
    node_ids = [
        node.node_id
        for node in graph.nodes
    ]

    node_id_set = set(node_ids)

    duplicate_node_ids = _find_duplicates(
        node_ids
    )

    missing_source_nodes: list[str] = []
    missing_target_nodes: list[str] = []

    edge_keys: list[str] = []
    connected_node_ids: set[str] = set()

    for edge in graph.edges:
        edge_key = (
            f"{edge.source_node_id}|"
            f"{edge.target_node_id}|"
            f"{edge.relation}"
        )

        edge_keys.append(edge_key)

        if edge.source_node_id not in node_id_set:
            missing_source_nodes.append(
                edge.source_node_id
            )
        else:
            connected_node_ids.add(
                edge.source_node_id
            )

        if edge.target_node_id not in node_id_set:
            missing_target_nodes.append(
                edge.target_node_id
            )
        else:
            connected_node_ids.add(
                edge.target_node_id
            )

    duplicate_edges = _find_duplicates(
        edge_keys
    )

    orphan_nodes = tuple(
        sorted(
            node_id_set - connected_node_ids
        )
    )

    cycles = find_cycles(graph)

    valid = not any(
        (
            duplicate_node_ids,
            duplicate_edges,
            missing_source_nodes,
            missing_target_nodes,
            cycles,
        )
    )

    return GraphValidation(
        valid=valid,
        duplicate_node_ids=tuple(
            duplicate_node_ids
        ),
        duplicate_edges=tuple(
            duplicate_edges
        ),
        missing_source_nodes=tuple(
            sorted(set(missing_source_nodes))
        ),
        missing_target_nodes=tuple(
            sorted(set(missing_target_nodes))
        ),
        orphan_nodes=orphan_nodes,
        cycles=cycles,
    )


def _find_duplicates(
    values: list[str],
) -> list[str]:
    seen: set[str] = set()
    duplicates: set[str] = set()

    for value in values:
        if value in seen:
            duplicates.add(value)
        else:
            seen.add(value)

    return sorted(duplicates)