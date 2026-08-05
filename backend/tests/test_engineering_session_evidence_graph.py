from app.brain.engineering_session import (
    EngineeringSession,
)
from app.brain.evidence_contracts import (
    EngineeringEvidence,
    EvidenceCategory,
    EvidenceValidity,
)
from app.brain.evidence_graph_builder import (
    build_evidence_graph,
)


def test_engineering_session_accepts_empty_evidence_graph():
    session = EngineeringSession()

    graph = build_evidence_graph([])

    session.set_evidence_graph(
        graph.model_dump()
    )

    assert session.evidence_graph is not None
    assert session.evidence_graph["nodes"] == []
    assert session.evidence_graph["edges"] == []
    assert session.evidence_graph["shadow_only"] is True
    assert (
        session.evidence_graph["affects_reasoning"]
        is False
    )
    assert (
        session.evidence_graph["affects_decision"]
        is False
    )


def test_engineering_session_serializes_evidence_graph():
    session = EngineeringSession()

    evidence = EngineeringEvidence(
        evidence_id="physics:differential_current",
        evidence_type="differential_current",
        category=EvidenceCategory.PHYSICS,
        source="transformer_physics",
        validity=EvidenceValidity.VALID,
    )

    graph = build_evidence_graph([evidence])

    session.set_evidence_graph(
        graph.model_dump()
    )

    serialized = session.to_dict()

    assert serialized["evidence_graph"] is not None
    assert len(
        serialized["evidence_graph"]["nodes"]
    ) == 1
    assert (
        serialized["evidence_graph"]["nodes"][0][
            "evidence_id"
        ]
        == "physics:differential_current"
    )
    assert (
        serialized["evidence_graph"]["edges"]
        == []
    )
    assert (
        serialized["evidence_graph"][
            "affects_reasoning"
        ]
        is False
    )
    assert (
        serialized["evidence_graph"][
            "affects_decision"
        ]
        is False
    )