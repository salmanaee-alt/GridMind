from __future__ import annotations

from typing import Any

from app.brain.engineering_session import (
    EngineeringSession,
)
from app.graph.builder import (
    GraphBuilder,
)
from app.graph.contracts import (
    GraphEdge,
    GraphNode,
)
from app.lineage.contracts import (
    LineageEdge,
    LineageGraph,
    LineageNode,
    LineageNodeType,
    LineageReference,
    LineageRelation,
)


def _build_nodes(
    session: EngineeringSession,
) -> list[LineageNode]:
    nodes: list[LineageNode] = []

    for index, item in enumerate(session.evidence):
        nodes.append(
            LineageNode(
                node_id=f"evidence:{index}",
                node_type=LineageNodeType.EVIDENCE,
                display_name=_display_name(
                    item,
                    fallback=f"Evidence {index + 1}",
                ),
                metadata={
                    "session_collection": "evidence",
                    "session_index": index,
                },
            )
        )

    for index, item in enumerate(session.hypotheses):
        nodes.append(
            LineageNode(
                node_id=f"hypothesis:{index}",
                node_type=LineageNodeType.HYPOTHESIS,
                display_name=_display_name(
                    item,
                    fallback=f"Hypothesis {index + 1}",
                ),
                metadata={
                    "session_collection": "hypotheses",
                    "session_index": index,
                },
            )
        )

    for index, item in enumerate(
        session.reasoning_steps
    ):
        nodes.append(
            LineageNode(
                node_id=f"reasoning:{index}",
                node_type=(
                    LineageNodeType.REASONING_STEP
                ),
                display_name=_display_name(
                    item,
                    fallback=(
                        f"Reasoning Step {index + 1}"
                    ),
                ),
                metadata={
                    "session_collection": (
                        "reasoning_steps"
                    ),
                    "session_index": index,
                },
            )
        )

    for index, item in enumerate(session.decisions):
        nodes.append(
            LineageNode(
                node_id=f"decision:{index}",
                node_type=LineageNodeType.DECISION,
                display_name=_display_name(
                    item,
                    fallback=f"Decision {index + 1}",
                ),
                metadata={
                    "session_collection": "decisions",
                    "session_index": index,
                },
            )
        )

    return nodes


def _display_name(
    item: Any,
    *,
    fallback: str,
) -> str:
    if not isinstance(item, dict):
        return fallback

    for key in (
        "display_name",
        "evidence_type",
        "hypothesis",
        "stage",
        "decision_type",
        "decision",
        "name",
        "type",
    ):
        value = item.get(key)

        if isinstance(value, str) and value.strip():
            return value.strip()

    return fallback


def _extract_references(
    item: Any,
) -> tuple[LineageReference, ...]:
    if not isinstance(item, dict):
        return ()

    raw_references = item.get(
        "lineage_references",
        (),
    )

    if raw_references is None:
        return ()

    references: list[LineageReference] = []

    for raw_reference in raw_references:
        references.append(
            LineageReference.model_validate(
                raw_reference
            )
        )

    return tuple(references)


def _build_edges(
    session: EngineeringSession,
    *,
    known_node_ids: set[str],
) -> list[LineageEdge]:
    edges: list[LineageEdge] = []

    collections = (
        ("evidence", session.evidence),
        ("hypothesis", session.hypotheses),
        ("reasoning", session.reasoning_steps),
        ("decision", session.decisions),
    )

    for node_prefix, items in collections:
        for index, item in enumerate(items):
            source_node_id = (
                f"{node_prefix}:{index}"
            )

            for reference in _extract_references(item):
                if (
                    reference.target_node_id
                    not in known_node_ids
                ):
                    continue

                edges.append(
                    LineageEdge(
                        source_node=source_node_id,
                        target_node=(
                            reference.target_node_id
                        ),
                        relation=reference.relation,
                        metadata={
                            "rationale": (
                                reference.rationale
                            ),
                            "source": reference.source,
                            **reference.metadata,
                        },
                    )
                )

    return edges


def _to_graph_node(
    node: LineageNode,
) -> GraphNode:
    return GraphNode(
        node_id=node.node_id,
        node_type=node.node_type.value,
        metadata={
            "display_name": node.display_name,
            **node.metadata,
        },
    )


def _to_graph_edge(
    edge: LineageEdge,
) -> GraphEdge:
    return GraphEdge(
        source_node_id=edge.source_node,
        target_node_id=edge.target_node,
        relation=edge.relation.value,
        metadata=edge.metadata,
    )


def build_lineage_graph(
    session: EngineeringSession,
) -> LineageGraph:
    lineage_nodes = _build_nodes(session)

    known_node_ids = {
        node.node_id
        for node in lineage_nodes
    }

    lineage_edges = _build_edges(
        session,
        known_node_ids=known_node_ids,
    )

    engineering_graph = (
        GraphBuilder()
        .set_graph_id(
            f"lineage:{session.session_id}"
        )
        .set_metadata(
            graph_type="engineering_lineage",
            session_id=session.session_id,
        )
        .add_nodes(
            tuple(
                _to_graph_node(node)
                for node in lineage_nodes
            )
        )
        .add_edges(
            tuple(
                _to_graph_edge(edge)
                for edge in lineage_edges
            )
        )
        .build()
    )

    return LineageGraph(
        nodes=tuple(
            LineageNode(
                node_id=node.node_id,
                node_type=LineageNodeType(
                    node.node_type
                ),
                display_name=str(
                    node.metadata.get(
                        "display_name",
                        node.node_id,
                    )
                ),
                metadata={
                    key: value
                    for key, value
                    in node.metadata.items()
                    if key != "display_name"
                },
            )
            for node in engineering_graph.nodes
        ),
        edges=tuple(
            LineageEdge(
                source_node=edge.source_node_id,
                target_node=edge.target_node_id,
                relation=LineageRelation(
                    edge.relation
                ),
                metadata=edge.metadata,
            )
            for edge in engineering_graph.edges
        ),
    )