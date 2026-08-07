from __future__ import annotations

from collections import deque

from app.graph.contracts import (
    EngineeringGraph,
)


def build_adjacency(
    graph: EngineeringGraph,
) -> dict[str, set[str]]:
    adjacency = {
        node.node_id: set()
        for node in graph.nodes
    }

    for edge in graph.edges:
        if edge.source_node_id in adjacency:
            adjacency[
                edge.source_node_id
            ].add(
                edge.target_node_id
            )

    return adjacency


def depth_first_traversal(
    graph: EngineeringGraph,
    *,
    start_node_id: str,
) -> tuple[str, ...]:
    adjacency = build_adjacency(graph)

    if start_node_id not in adjacency:
        return ()

    visited: set[str] = set()
    order: list[str] = []

    def visit(node_id: str) -> None:
        if node_id in visited:
            return

        visited.add(node_id)
        order.append(node_id)

        for child in sorted(
            adjacency[node_id]
        ):
            visit(child)

    visit(start_node_id)

    return tuple(order)


def breadth_first_traversal(
    graph: EngineeringGraph,
    *,
    start_node_id: str,
) -> tuple[str, ...]:
    adjacency = build_adjacency(graph)

    if start_node_id not in adjacency:
        return ()

    visited = {start_node_id}

    queue = deque(
        [start_node_id]
    )

    order: list[str] = []

    while queue:
        node = queue.popleft()

        order.append(node)

        for child in sorted(
            adjacency[node]
        ):
            if child in visited:
                continue

            visited.add(child)
            queue.append(child)

    return tuple(order)