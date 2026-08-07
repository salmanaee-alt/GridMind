from __future__ import annotations

from collections import deque

from app.graph.algorithms.traversal import (
    build_adjacency,
)
from app.graph.contracts import (
    EngineeringGraph,
)


def topological_sort(
    graph: EngineeringGraph,
) -> tuple[str, ...]:
    adjacency = build_adjacency(graph)

    in_degree: dict[str, int] = {
        node_id: 0
        for node_id in adjacency
    }

    for source_node_id, targets in adjacency.items():
        for target_node_id in targets:
            if target_node_id in in_degree:
                in_degree[target_node_id] += 1

    queue = deque(
        sorted(
            node_id
            for node_id, degree in in_degree.items()
            if degree == 0
        )
    )

    order: list[str] = []

    while queue:
        node_id = queue.popleft()
        order.append(node_id)

        for target_node_id in sorted(
            adjacency[node_id]
        ):
            if target_node_id not in in_degree:
                continue

            in_degree[target_node_id] -= 1

            if in_degree[target_node_id] == 0:
                queue.append(target_node_id)

    if len(order) != len(adjacency):
        return ()

    return tuple(order)