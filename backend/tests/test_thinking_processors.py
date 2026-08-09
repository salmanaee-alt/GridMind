from app.thinking.contracts import (
    ThinkingStage,
    ThinkingState,
)
from app.thinking.processors.observe import (
    ObserveProcessor,
)
from app.thinking.processors.understand import (
    UnderstandProcessor,
)
from app.thinking.processors.validate import (
    ValidateProcessor,
)
from app.thinking.processors.hypothesize import (
    HypothesizeProcessor,
)
from app.thinking.processors.rank_evidence import (
    RankEvidenceProcessor,
)
from app.thinking.processors.resolve_conflicts import (
    ResolveConflictsProcessor,
)
from app.thinking.processors.verify_physics import (
    VerifyPhysicsProcessor,
)
from app.thinking.processors.safety_gate import (
    SafetyGateProcessor,
)
from app.thinking.processors.decide import (
    DecideProcessor,
)
from app.thinking.processors.explain import (
    ExplainProcessor,
)
from app.thinking.processors.learn import (
    LearnProcessor,
)
from app.brain.evidence_graph_contracts import (
    EvidenceEdge,
    EvidenceGraph,
    EvidenceNode,
    EvidenceRelation,
)
from app.thinking.graph_context import (
    ThinkingGraphContext,
)
from app.lineage.contracts import (
    LineageEdge,
    LineageGraph,
    LineageNode,
    LineageNodeType,
    LineageRelation,
)
    

def test_observe_processor_reports_observation_count():
    state = ThinkingState(
        session_id="session-1",
        observations=(
            {"type": "relay_event"},
            {"type": "comtrade"},
        ),
    )

    result = ObserveProcessor().execute(state)

    assert (
        result.metadata[
            "observe_stage"
        ]["observation_count"]
        == 2
    )

    assert (
        result.metadata[
            "observe_stage"
        ]["has_observations"]
        is True
    )


def test_observe_processor_handles_empty_state():
    state = ThinkingState(
        session_id="session-1",
    )

    result = ObserveProcessor().execute(state)

    assert (
        result.metadata[
            "observe_stage"
        ]["observation_count"]
        == 0
    )

    assert (
        result.metadata[
            "observe_stage"
        ]["has_observations"]
        is False
    )


def test_understand_processor_reports_context_counts():
    state = ThinkingState(
        session_id="session-1",
        observations=(
            {"type": "relay_event"},
        ),
        evidence=(
            {"evidence_id": "e1"},
        ),
        hypotheses=(
            {"hypothesis": "internal_fault"},
        ),
    )

    result = UnderstandProcessor().execute(
        state
    )

    metadata = result.metadata[
        "understand_stage"
    ]

    assert metadata["evidence_count"] == 1
    assert metadata["hypothesis_count"] == 1
    assert (
        metadata["has_engineering_context"]
        is True
    )


def test_understand_processor_handles_empty_state():
    state = ThinkingState(
        session_id="session-1",
    )

    result = UnderstandProcessor().execute(
        state
    )

    metadata = result.metadata[
        "understand_stage"
    ]

    assert metadata["evidence_count"] == 0
    assert metadata["hypothesis_count"] == 0
    assert (
        metadata["has_engineering_context"]
        is False
    )


def test_processors_do_not_change_current_stage():
    state = ThinkingState(
        session_id="session-1",
        current_stage=ThinkingStage.OBSERVE,
    )

    result = ObserveProcessor().execute(state)

    assert result.current_stage == (
        ThinkingStage.OBSERVE
    )


def test_processors_preserve_shadow_safety_flags():
    state = ThinkingState(
        session_id="session-1",
    )

    observed = ObserveProcessor().execute(
        state
    )

    understood = (
        UnderstandProcessor().execute(
            observed
        )
    )

    assert understood.shadow_only is True
    assert (
        understood.affects_reasoning
        is False
    )
    assert (
        understood.affects_decision
        is False
    )


def test_validate_processor_reports_available_evidence():
    state = ThinkingState(
        session_id="session-1",
        evidence=(
            {
                "evidence_id": "e1",
            },
        ),
    )

    result = ValidateProcessor().execute(
        state
    )

    metadata = result.metadata[
        "validate_stage"
    ]

    assert metadata["evidence_count"] == 1
    assert metadata["has_evidence"] is True
    assert (
        metadata["validation_status"]
        == "available"
    )


def test_validate_processor_reports_insufficient_evidence():
    state = ThinkingState(
        session_id="session-1",
    )

    result = ValidateProcessor().execute(
        state
    )

    metadata = result.metadata[
        "validate_stage"
    ]

    assert metadata["evidence_count"] == 0
    assert metadata["has_evidence"] is False
    assert (
        metadata["validation_status"]
        == "insufficient"
    )


def test_validate_processor_preserves_shadow_safety():
    state = ThinkingState(
        session_id="session-1",
    )

    result = ValidateProcessor().execute(
        state
    )

    assert result.shadow_only is True
    assert result.affects_reasoning is False
    assert result.affects_decision is False


def test_hypothesize_processor_reports_existing_hypotheses():
    state = ThinkingState(
        session_id="session-1",
        hypotheses=(
            {
                "hypothesis": "internal_fault",
            },
            {
                "hypothesis": "ct_saturation",
            },
        ),
    )

    result = HypothesizeProcessor().execute(
        state
    )

    metadata = result.metadata[
        "hypothesize_stage"
    ]

    assert metadata["hypothesis_count"] == 2
    assert metadata["has_hypotheses"] is True
    assert (
        metadata["generation_status"]
        == "available"
    )


def test_hypothesize_processor_reports_missing_hypotheses():
    state = ThinkingState(
        session_id="session-1",
    )

    result = HypothesizeProcessor().execute(
        state
    )

    metadata = result.metadata[
        "hypothesize_stage"
    ]

    assert metadata["hypothesis_count"] == 0
    assert metadata["has_hypotheses"] is False
    assert (
        metadata["generation_status"]
        == "not_generated"
    )


def test_hypothesize_processor_preserves_shadow_safety():
    state = ThinkingState(
        session_id="session-1",
    )

    result = HypothesizeProcessor().execute(
        state
    )

    assert result.shadow_only is True
    assert result.affects_reasoning is False
    assert result.affects_decision is False


def test_rank_evidence_processor_orders_by_confidence():
    state = ThinkingState(
        session_id="session-1",
        evidence=(
            {
                "evidence_id": "e1",
                "confidence": 0.4,
            },
            {
                "evidence_id": "e2",
                "confidence": 0.9,
            },
            {
                "evidence_id": "e3",
                "confidence": 0.7,
            },
        ),
    )

    result = RankEvidenceProcessor().execute(
        state
    )

    metadata = result.metadata[
        "rank_evidence_stage"
    ]

    assert metadata["ranked_count"] == 3
    assert metadata["unranked_count"] == 0

    assert metadata["ranking"] == (
        {
            "evidence_index": 1,
            "confidence": 0.9,
        },
        {
            "evidence_index": 2,
            "confidence": 0.7,
        },
        {
            "evidence_index": 0,
            "confidence": 0.4,
        },
    )


def test_rank_evidence_processor_reports_unranked_items():
    state = ThinkingState(
        session_id="session-1",
        evidence=(
            {
                "evidence_id": "e1",
            },
            {
                "evidence_id": "e2",
                "confidence": 0.8,
            },
        ),
    )

    result = RankEvidenceProcessor().execute(
        state
    )

    metadata = result.metadata[
        "rank_evidence_stage"
    ]

    assert metadata["evidence_count"] == 2
    assert metadata["ranked_count"] == 1
    assert metadata["unranked_count"] == 1
    assert (
        metadata["ranking_status"]
        == "available"
    )


def test_rank_evidence_processor_handles_missing_confidence():
    state = ThinkingState(
        session_id="session-1",
        evidence=(
            {
                "evidence_id": "e1",
            },
        ),
    )

    result = RankEvidenceProcessor().execute(
        state
    )

    metadata = result.metadata[
        "rank_evidence_stage"
    ]

    assert metadata["ranked_count"] == 0
    assert metadata["unranked_count"] == 1
    assert (
        metadata["ranking_status"]
        == "insufficient_metadata"
    )


def test_rank_evidence_processor_preserves_shadow_safety():
    state = ThinkingState(
        session_id="session-1",
    )

    result = RankEvidenceProcessor().execute(
        state
    )

    assert result.shadow_only is True
    assert result.affects_reasoning is False
    assert result.affects_decision is False


def test_resolve_conflicts_processor_detects_evidence_conflicts():
    state = ThinkingState(
        session_id="session-1",
        evidence=(
            {
                "evidence_id": "e1",
                "conflicts": (
                    "current_mismatch",
                ),
            },
        ),
    )

    result = ResolveConflictsProcessor().execute(
        state
    )

    metadata = result.metadata[
        "resolve_conflicts_stage"
    ]

    assert metadata["conflict_count"] == 1
    assert metadata["has_conflicts"] is True
    assert (
        metadata["resolution_status"]
        == "requires_review"
    )

    assert metadata["conflicts"] == (
        {
            "source_type": "evidence",
            "source_index": 0,
            "conflict": "current_mismatch",
        },
    )


def test_resolve_conflicts_processor_detects_hypothesis_conflicts():
    state = ThinkingState(
        session_id="session-1",
        hypotheses=(
            {
                "hypothesis": "internal_fault",
                "conflicts": [
                    "harmonic_restraint_active",
                ],
            },
        ),
    )

    result = ResolveConflictsProcessor().execute(
        state
    )

    metadata = result.metadata[
        "resolve_conflicts_stage"
    ]

    assert metadata["conflict_count"] == 1

    assert metadata["conflicts"][0][
        "source_type"
    ] == "hypothesis"


def test_resolve_conflicts_processor_handles_no_conflicts():
    state = ThinkingState(
        session_id="session-1",
        evidence=(
            {
                "evidence_id": "e1",
            },
        ),
    )

    result = ResolveConflictsProcessor().execute(
        state
    )

    metadata = result.metadata[
        "resolve_conflicts_stage"
    ]

    assert metadata["conflict_count"] == 0
    assert metadata["has_conflicts"] is False
    assert (
        metadata["resolution_status"]
        == "no_conflicts"
    )


def test_resolve_conflicts_processor_preserves_shadow_safety():
    state = ThinkingState(
        session_id="session-1",
    )

    result = ResolveConflictsProcessor().execute(
        state
    )

    assert result.shadow_only is True
    assert result.affects_reasoning is False
    assert result.affects_decision is False


def test_verify_physics_processor_reports_verified_checks():
    state = ThinkingState(
        session_id="session-1",
        physics_checks=(
            {
                "status": "valid",
            },
            {
                "status": "valid",
            },
        ),
    )

    result = VerifyPhysicsProcessor().execute(
        state
    )

    metadata = result.metadata[
        "verify_physics_stage"
    ]

    assert metadata["check_count"] == 2
    assert metadata["valid_count"] == 2
    assert metadata["invalid_count"] == 0
    assert metadata["unknown_count"] == 0
    assert (
        metadata["verification_status"]
        == "verified"
    )


def test_verify_physics_processor_detects_physics_conflict():
    state = ThinkingState(
        session_id="session-1",
        physics_checks=(
            {
                "status": "valid",
            },
            {
                "status": "invalid",
            },
        ),
    )

    result = VerifyPhysicsProcessor().execute(
        state
    )

    metadata = result.metadata[
        "verify_physics_stage"
    ]

    assert metadata["invalid_count"] == 1
    assert (
        metadata["verification_status"]
        == "physics_conflict"
    )


def test_verify_physics_processor_reports_incomplete_checks():
    state = ThinkingState(
        session_id="session-1",
        physics_checks=(
            {
                "status": "valid",
            },
            {
                "status": "unknown",
            },
        ),
    )

    result = VerifyPhysicsProcessor().execute(
        state
    )

    metadata = result.metadata[
        "verify_physics_stage"
    ]

    assert metadata["unknown_count"] == 1
    assert (
        metadata["verification_status"]
        == "incomplete"
    )


def test_verify_physics_processor_handles_no_checks():
    state = ThinkingState(
        session_id="session-1",
    )

    result = VerifyPhysicsProcessor().execute(
        state
    )

    metadata = result.metadata[
        "verify_physics_stage"
    ]

    assert metadata["check_count"] == 0
    assert (
        metadata["verification_status"]
        == "not_available"
    )


def test_verify_physics_processor_preserves_shadow_safety():
    state = ThinkingState(
        session_id="session-1",
    )

    result = VerifyPhysicsProcessor().execute(
        state
    )

    assert result.shadow_only is True
    assert result.affects_reasoning is False
    assert result.affects_decision is False


def test_safety_gate_reports_no_blocking_findings():
    state = ThinkingState(
        session_id="session-1",
        safety_findings=(
            {
                "severity": "low",
            },
        ),
    )

    result = SafetyGateProcessor().execute(
        state
    )

    metadata = result.metadata[
        "safety_gate_stage"
    ]

    assert metadata["finding_count"] == 1
    assert metadata["low_count"] == 1
    assert (
        metadata["safety_status"]
        == "no_blocking_findings"
    )
    assert metadata["advisory_only"] is True


def test_safety_gate_detects_medium_findings():
    state = ThinkingState(
        session_id="session-1",
        safety_findings=(
            {
                "severity": "medium",
            },
        ),
    )

    result = SafetyGateProcessor().execute(
        state
    )

    metadata = result.metadata[
        "safety_gate_stage"
    ]

    assert metadata["medium_count"] == 1
    assert (
        metadata["safety_status"]
        == "medium_findings"
    )


def test_safety_gate_detects_high_findings():
    state = ThinkingState(
        session_id="session-1",
        safety_findings=(
            {
                "severity": "high",
            },
        ),
    )

    result = SafetyGateProcessor().execute(
        state
    )

    metadata = result.metadata[
        "safety_gate_stage"
    ]

    assert metadata["high_count"] == 1
    assert (
        metadata["safety_status"]
        == "high_findings"
    )


def test_safety_gate_detects_critical_findings():
    state = ThinkingState(
        session_id="session-1",
        safety_findings=(
            {
                "severity": "critical",
            },
        ),
    )

    result = SafetyGateProcessor().execute(
        state
    )

    metadata = result.metadata[
        "safety_gate_stage"
    ]

    assert metadata["critical_count"] == 1
    assert (
        metadata["safety_status"]
        == "critical_findings"
    )


def test_safety_gate_handles_unknown_severity():
    state = ThinkingState(
        session_id="session-1",
        safety_findings=(
            {
                "severity": "unexpected",
            },
        ),
    )

    result = SafetyGateProcessor().execute(
        state
    )

    metadata = result.metadata[
        "safety_gate_stage"
    ]

    assert metadata["unknown_count"] == 1
    assert (
        metadata["safety_status"]
        == "incomplete"
    )


def test_safety_gate_handles_no_findings():
    state = ThinkingState(
        session_id="session-1",
    )

    result = SafetyGateProcessor().execute(
        state
    )

    metadata = result.metadata[
        "safety_gate_stage"
    ]

    assert metadata["finding_count"] == 0
    assert (
        metadata["safety_status"]
        == "not_available"
    )


def test_safety_gate_preserves_shadow_safety():
    state = ThinkingState(
        session_id="session-1",
    )

    result = SafetyGateProcessor().execute(
        state
    )

    assert result.shadow_only is True
    assert result.affects_reasoning is False
    assert result.affects_decision is False


def test_decide_processor_reports_existing_decision():
    state = ThinkingState(
        session_id="session-1",
        decisions=(
            {
                "decision": "investigate_internal_fault",
            },
        ),
    )

    result = DecideProcessor().execute(
        state
    )

    metadata = result.metadata[
        "decide_stage"
    ]

    assert metadata["decision_count"] == 1
    assert metadata["has_decisions"] is True
    assert (
        metadata["decision_status"]
        == "available"
    )
    assert metadata["advisory_only"] is True
    assert (
        metadata["execution_authorized"]
        is False
    )


def test_decide_processor_reports_missing_decision():
    state = ThinkingState(
        session_id="session-1",
    )

    result = DecideProcessor().execute(
        state
    )

    metadata = result.metadata[
        "decide_stage"
    ]

    assert metadata["decision_count"] == 0
    assert metadata["has_decisions"] is False
    assert (
        metadata["decision_status"]
        == "not_available"
    )


def test_decide_processor_does_not_create_decision():
    state = ThinkingState(
        session_id="session-1",
    )

    result = DecideProcessor().execute(
        state
    )

    assert result.decisions == ()


def test_decide_processor_does_not_authorize_execution():
    state = ThinkingState(
        session_id="session-1",
        decisions=(
            {
                "decision": "reenergize",
            },
        ),
    )

    result = DecideProcessor().execute(
        state
    )

    metadata = result.metadata[
        "decide_stage"
    ]

    assert (
        metadata["execution_authorized"]
        is False
    )


def test_decide_processor_preserves_shadow_safety():
    state = ThinkingState(
        session_id="session-1",
    )

    result = DecideProcessor().execute(
        state
    )

    assert result.shadow_only is True
    assert result.affects_reasoning is False
    assert result.affects_decision is False


def test_explain_processor_builds_structured_summary():
    state = ThinkingState(
        session_id="session-1",
        observations=(
            {"type": "relay_event"},
        ),
        evidence=(
            {"evidence_id": "e1"},
            {"evidence_id": "e2"},
        ),
        hypotheses=(
            {"hypothesis": "internal_fault"},
        ),
        physics_checks=(
            {"status": "valid"},
        ),
        safety_findings=(
            {"severity": "low"},
        ),
        decisions=(
            {"decision": "investigate"},
        ),
    )

    result = ExplainProcessor().execute(
        state
    )

    assert len(result.explanations) == 1

    explanation = result.explanations[0]

    assert (
        explanation["type"]
        == "structured_engineering_summary"
    )

    assert explanation["summary"] == {
        "observation_count": 1,
        "evidence_count": 2,
        "hypothesis_count": 1,
        "physics_check_count": 1,
        "safety_finding_count": 1,
        "decision_count": 1,
        "lineage_node_count": 0,
        "lineage_edge_count": 0,
    }

    assert (
        explanation["free_text_generated"]
        is False
    )


def test_explain_processor_handles_empty_state():
    state = ThinkingState(
        session_id="session-1",
    )

    result = ExplainProcessor().execute(
        state
    )

    metadata = result.metadata[
        "explain_stage"
    ]

    assert result.explanations == ()
    assert (
        metadata["explanation_available"]
        is False
    )
    assert metadata["explanation_count"] == 0


def test_explain_processor_preserves_existing_explanations():
    state = ThinkingState(
        session_id="session-1",
        observations=(
            {"type": "relay_event"},
        ),
        explanations=(
            {
                "type": "existing",
            },
        ),
    )

    result = ExplainProcessor().execute(
        state
    )

    assert len(result.explanations) == 2

    assert result.explanations[0] == {
        "type": "existing",
    }


def test_explain_processor_does_not_generate_free_text():
    state = ThinkingState(
        session_id="session-1",
        evidence=(
            {"evidence_id": "e1"},
        ),
    )

    result = ExplainProcessor().execute(
        state
    )

    metadata = result.metadata[
        "explain_stage"
    ]

    assert (
        metadata["free_text_generated"]
        is False
    )

    assert (
        result.explanations[0][
            "free_text_generated"
        ]
        is False
    )


def test_explain_processor_preserves_shadow_safety():
    state = ThinkingState(
        session_id="session-1",
    )

    result = ExplainProcessor().execute(
        state
    )

    assert result.shadow_only is True
    assert result.affects_reasoning is False
    assert result.affects_decision is False


def test_learn_processor_extracts_learning_candidates():
    state = ThinkingState(
        session_id="session-1",
        decisions=(
            {
                "decision": "investigate",
            },
        ),
        safety_findings=(
            {
                "severity": "high",
            },
        ),
    )

    result = LearnProcessor().execute(
        state
    )

    assert len(result.learning_items) == 2

    assert (
        result.learning_items[0][
            "source_type"
        ]
        == "decision"
    )

    assert (
        result.learning_items[1][
            "source_type"
        ]
        == "safety_finding"
    )


def test_learn_processor_requires_review():
    state = ThinkingState(
        session_id="session-1",
        decisions=(
            {
                "decision": "investigate",
            },
        ),
    )

    result = LearnProcessor().execute(
        state
    )

    candidate = result.learning_items[0]

    assert candidate["review_required"] is True
    assert (
        candidate["memory_write_authorized"]
        is False
    )


def test_learn_processor_does_not_authorize_memory_write():
    state = ThinkingState(
        session_id="session-1",
        explanations=(
            {
                "type": "structured_summary",
            },
        ),
    )

    result = LearnProcessor().execute(
        state
    )

    metadata = result.metadata[
        "learn_stage"
    ]

    assert (
        metadata["memory_write_authorized"]
        is False
    )


def test_learn_processor_handles_empty_state():
    state = ThinkingState(
        session_id="session-1",
    )

    result = LearnProcessor().execute(
        state
    )

    metadata = result.metadata[
        "learn_stage"
    ]

    assert result.learning_items == ()
    assert metadata["candidate_count"] == 0
    assert (
        metadata["learning_status"]
        == "no_candidates"
    )


def test_learn_processor_preserves_existing_learning_items():
    state = ThinkingState(
        session_id="session-1",
        learning_items=(
            {
                "existing": True,
            },
        ),
        decisions=(
            {
                "decision": "investigate",
            },
        ),
    )

    result = LearnProcessor().execute(
        state
    )

    assert len(result.learning_items) == 2
    assert result.learning_items[0] == {
        "existing": True,
    }


def test_learn_processor_preserves_shadow_safety():
    state = ThinkingState(
        session_id="session-1",
    )

    result = LearnProcessor().execute(
        state
    )

    assert result.shadow_only is True
    assert result.affects_reasoning is False
    assert result.affects_decision is False


def test_rank_evidence_processor_reports_graph_context_usage():
    state = ThinkingState(
        session_id="session-1",
        evidence=(
            {
                "evidence_id": "e1",
                "confidence": 0.9,
            },
        ),
        graph_context=ThinkingGraphContext(
            evidence_graph=EvidenceGraph(
                nodes=[
                    EvidenceNode(
                        node_id="evidence-node:e1",
                        evidence_id="e1",
                        evidence_type="test",
                        category="physics",
                    ),
                ],
            ),
        ),
    )

    result = RankEvidenceProcessor().execute(
        state
    )

    metadata = result.metadata[
        "rank_evidence_stage"
    ]

    assert (
        metadata["graph_context_used"]
        is True
    )

    assert (
        metadata["graph_node_count"]
        == 1
    )


def test_resolve_conflicts_processor_reads_graph_conflicts():
    state = ThinkingState(
        session_id="session-1",
        graph_context=ThinkingGraphContext(
            evidence_graph=EvidenceGraph(
                nodes=[
                    EvidenceNode(
                        node_id="evidence-node:e1",
                        evidence_id="e1",
                        evidence_type="test",
                        category="physics",
                    ),
                    EvidenceNode(
                        node_id="evidence-node:e2",
                        evidence_id="e2",
                        evidence_type="test",
                        category="measurement",
                    ),
                ],
                edges=[
                    EvidenceEdge(
                        source_node="evidence-node:e1",
                        target_node="evidence-node:e2",
                        relation=(
                            EvidenceRelation.CONTRADICTS
                        ),
                    ),
                ],
            ),
        ),
    )

    result = (
        ResolveConflictsProcessor()
        .execute(state)
    )

    metadata = result.metadata[
        "resolve_conflicts_stage"
    ]

    assert (
        metadata["graph_context_used"]
        is True
    )

    assert (
        metadata["graph_conflict_count"]
        == 1
    )

    assert metadata["graph_conflicts"] == (
        {
            "source_node": "evidence-node:e1",
            "target_node": "evidence-node:e2",
            "relation": "contradicts",
        },
    )


def test_explain_processor_reads_lineage_graph():
    state = ThinkingState(
        session_id="session-1",
        observations=(
            {
                "type": "relay_event",
            },
        ),
        graph_context=ThinkingGraphContext(
            lineage_graph=LineageGraph(
                nodes=(
                    LineageNode(
                        node_id="evidence:0",
                        node_type=(
                            LineageNodeType.EVIDENCE
                        ),
                        display_name=(
                            "Evidence 1"
                        ),
                    ),
                    LineageNode(
                        node_id="decision:0",
                        node_type=(
                            LineageNodeType.DECISION
                        ),
                        display_name=(
                            "Decision 1"
                        ),
                    ),
                ),
            ),
        ),
    )

    result = ExplainProcessor().execute(
        state
    )

    metadata = result.metadata[
        "explain_stage"
    ]

    assert (
        metadata["graph_context_used"]
        is True
    )

    assert metadata[
        "lineage_node_count"
    ] == 2

    assert metadata[
        "lineage_edge_count"
    ] == 0

    assert (
        result.explanations[0][
            "lineage_context"
        ]["available"]
        is True
    )


def test_understand_processor_reports_graph_metrics():
    state = ThinkingState(
        session_id="session-1",
        graph_context=ThinkingGraphContext(
            evidence_graph=EvidenceGraph(
                nodes=[
                    EvidenceNode(
                        node_id="e1",
                        evidence_id="e1",
                        evidence_type="physics",
                        category="physics",
                    ),
                ],
            ),
            lineage_graph=LineageGraph(
                nodes=(
                    LineageNode(
                        node_id="decision:0",
                        node_type=LineageNodeType.DECISION,
                        display_name="Decision",
                    ),
                ),
            ),
        ),
    )

    result = (
        UnderstandProcessor()
        .execute(state)
    )

    metadata = result.metadata[
        "understand_stage"
    ]

    assert metadata["graph_context_used"] is True
    assert metadata["evidence_graph_nodes"] == 1
    assert metadata["evidence_graph_edges"] == 0
    assert metadata["lineage_graph_nodes"] == 1
    assert metadata["lineage_graph_edges"] == 0


def test_explain_processor_builds_decision_traceability():
    lineage_graph = LineageGraph(
        nodes=(
            LineageNode(
                node_id="decision:0",
                node_type=LineageNodeType.DECISION,
                display_name="Decision",
            ),
            LineageNode(
                node_id="hypothesis:0",
                node_type=LineageNodeType.HYPOTHESIS,
                display_name="Hypothesis",
            ),
            LineageNode(
                node_id="evidence:0",
                node_type=LineageNodeType.EVIDENCE,
                display_name="Evidence",
            ),
        ),
        edges=(
            LineageEdge(
                source_node="decision:0",
                target_node="hypothesis:0",
                relation=(
                    LineageRelation.DEPENDS_ON
                ),
            ),
            LineageEdge(
                source_node="hypothesis:0",
                target_node="evidence:0",
                relation=(
                    LineageRelation.SUPPORTS
                ),
            ),
        ),
    )

    state = ThinkingState(
        session_id="session-1",
        decisions=(
            {
                "decision": "investigate",
            },
        ),
        graph_context=ThinkingGraphContext(
            lineage_graph=lineage_graph,
        ),
    )

    result = ExplainProcessor().execute(
        state
    )

    lineage_context = (
        result.explanations[0][
            "lineage_context"
        ]
    )

    assert (
        lineage_context["traceability"]
        == (
            {
                "decision_node": "decision:0",
                "reachable_nodes": (
                    "decision:0",
                    "hypothesis:0",
                    "evidence:0",
                ),
                "reachable_count": 3,
            },
        )
    )

    assert (
        result.metadata[
            "explain_stage"
        ]["traceability_count"]
        == 1
    )