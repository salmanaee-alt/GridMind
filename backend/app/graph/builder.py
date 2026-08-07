from __future__ import annotations

from app.graph.contracts import (
    EngineeringGraph,
    GraphEdge,
    GraphNode,
)


class GraphBuilder:
    def __init__(self) -> None:
        self._graph_id = ""
        self._nodes: dict[str, GraphNode] = {}
        self._edges: dict[
            tuple[str, str, str],
            GraphEdge,
        ] = {}
        self._metadata: dict[str, object] = {}

    def set_graph_id(
        self,
        graph_id: str,
    ) -> "GraphBuilder":
        self._graph_id = graph_id
        return self

    def add_node(
        self,
        node: GraphNode,
    ) -> "GraphBuilder":
        self._nodes[node.node_id] = node
        return self

    def add_nodes(
        self,
        nodes: list[GraphNode] | tuple[GraphNode, ...],
    ) -> "GraphBuilder":
        for node in nodes:
            self.add_node(node)

        return self

    def add_edge(
        self,
        edge: GraphEdge,
    ) -> "GraphBuilder":
        key = (
            edge.source_node_id,
            edge.target_node_id,
            edge.relation,
        )

        self._edges[key] = edge

        return self

    def add_edges(
        self,
        edges: list[GraphEdge] | tuple[GraphEdge, ...],
    ) -> "GraphBuilder":
        for edge in edges:
            self.add_edge(edge)

        return self

    def set_metadata(
        self,
        **kwargs: object,
    ) -> "GraphBuilder":
        self._metadata.update(kwargs)
        return self

    def build(
        self,
    ) -> EngineeringGraph:
        return EngineeringGraph(
            graph_id=self._graph_id,
            nodes=tuple(
                sorted(
                    self._nodes.values(),
                    key=lambda node: node.node_id,
                )
            ),
            edges=tuple(
                sorted(
                    self._edges.values(),
                    key=lambda edge: (
                        edge.source_node_id,
                        edge.target_node_id,
                        edge.relation,
                    ),
                )
            ),
            metadata=dict(self._metadata),
        )