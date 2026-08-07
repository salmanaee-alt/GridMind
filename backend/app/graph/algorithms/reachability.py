from __future__ import annotations

from collections import deque

from app.graph.contracts import (
    EngineeringGraph,
)
from app.graph.algorithms.traversal import (
    build_adjacency,
)


def find_reachable_nodes(
    graph: EngineeringGraph,
    *,
    start_node_id: str,
) -> tuple[str, ...]:
    adjacency = build_adjacency(graph)

    if start_node_id not in adjacency:
        return ()

    visited = {start_node_id}
    queue = deque([start_node_id])

    reachable: list[str] = []

    while queue:
        node = queue.popleft()

        reachable.append(node)

        for child in sorted(adjacency[node]):
            if child in visited:
                continue

            visited.add(child)
            queue.append(child)

    return tuple(reachable)