from __future__ import annotations

from typing import Any

from app.brain.engineering_session import EngineeringSession
from app.lineage.contracts import (
    LineageEdge,
    LineageGraph,
    LineageNode,
    LineageNodeType,
    LineageReference,
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

    for index, item in enumerate(session.reasoning_steps):
        nodes.append(
            LineageNode(
                node_id=f"reasoning:{index}",
                node_type=LineageNodeType.REASONING_STEP,
                display_name=_display_name(
                    item,
                    fallback=f"Reasoning Step {index + 1}",
                ),
                metadata={
                    "session_collection": "reasoning_steps",
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


def build_lineage_graph(
    session: EngineeringSession,
) -> LineageGraph:
    nodes = _build_nodes(session)

    known_node_ids = {
        node.node_id
        for node in nodes
    }

    edges = _build_edges(
        session,
        known_node_ids=known_node_ids,
    )

    return LineageGraph(
        nodes=tuple(nodes),
        edges=tuple(edges),
    )