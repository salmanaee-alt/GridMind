from __future__ import annotations

from app.graph.contracts import (
    EngineeringGraph,
)


def build_undirected_adjacency(
    graph: EngineeringGraph,
) -> dict[str, set[str]]:
    adjacency: dict[str, set[str]] = {
        node.node_id: set()
        for node in graph.nodes
    }

    for edge in graph.edges:
        if (
            edge.source_node_id in adjacency
            and edge.target_node_id in adjacency
        ):
            adjacency[
                edge.source_node_id
            ].add(
                edge.target_node_id
            )

            adjacency[
                edge.target_node_id
            ].add(
                edge.source_node_id
            )

    return adjacency


def find_connected_components(
    graph: EngineeringGraph,
) -> tuple[tuple[str, ...], ...]:
    adjacency = build_undirected_adjacency(
        graph
    )

    visited: set[str] = set()
    components: list[tuple[str, ...]] = []

    for start_node_id in sorted(adjacency):
        if start_node_id in visited:
            continue

        stack = [start_node_id]
        component: list[str] = []

        while stack:
            node_id = stack.pop()

            if node_id in visited:
                continue

            visited.add(node_id)
            component.append(node_id)

            for neighbor in sorted(
                adjacency[node_id],
                reverse=True,
            ):
                if neighbor not in visited:
                    stack.append(neighbor)

        components.append(
            tuple(sorted(component))
        )

    return tuple(components)