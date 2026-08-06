from __future__ import annotations

from app.lineage.contracts import (
    LineageGraph,
)


def build_adjacency(
    graph: LineageGraph,
) -> dict[str, set[str]]:
    """
    Build an adjacency list from a LineageGraph.

    Every node always exists in the returned mapping,
    even if it has no outgoing edges.
    """

    adjacency: dict[str, set[str]] = {
        node.node_id: set()
        for node in graph.nodes
    }

    for edge in graph.edges:
        if edge.source_node in adjacency:
            adjacency[edge.source_node].add(
                edge.target_node
            )

    return adjacency


def find_cycles(
    graph: LineageGraph,
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