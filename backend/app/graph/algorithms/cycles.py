from __future__ import annotations

from app.graph.algorithms.traversal import (
    build_adjacency,
)
from app.graph.contracts import (
    EngineeringGraph,
)


def find_cycles(
    graph: EngineeringGraph,
) -> tuple[tuple[str, ...], ...]:
    adjacency = build_adjacency(graph)

    visited: set[str] = set()
    active: set[str] = set()
    path: list[str] = []
    cycles: list[tuple[str, ...]] = []

    def visit(node_id: str) -> None:
        if node_id in active:
            try:
                start_index = path.index(node_id)
            except ValueError:
                return

            cycle = tuple(
                path[start_index:] + [node_id]
            )

            if cycle not in cycles:
                cycles.append(cycle)

            return

        if node_id in visited:
            return

        visited.add(node_id)
        active.add(node_id)
        path.append(node_id)

        for target_node_id in sorted(
            adjacency.get(node_id, set())
        ):
            if target_node_id in adjacency:
                visit(target_node_id)

        path.pop()
        active.remove(node_id)

    for node_id in sorted(adjacency):
        visit(node_id)

    return tuple(cycles)