from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.brain.engineering_session import EngineeringSession, InvestigationStatus
from app.transformer.evidence_quality import score_evidence_quality


@dataclass
class StageResult:
    stage: str
    summary: str
    data: dict[str, Any]


class EngineeringBrain:
    CONFIDENCE_RANK = {
        "low": 1,
        "medium": 2,
        "high": 3,
    }

    def run(self, session: EngineeringSession) -> EngineeringSession:
        if session.status == InvestigationStatus.COMPLETED:
            session.add_reasoning_step({
                "stage": "brain_guard",
                "summary": "Session is already completed. No additional reasoning was executed.",
                "data": {
                    "status": session.status.value,
                },
            })
            return session

        session.set_status(InvestigationStatus.OBSERVING)
        session.add_reasoning_step({
            "stage": "observe",
            "summary": "Captured initial engineering observations.",
            "data": {
                "observation_count": len(session.observations),
            },
        })

        available_evidence = self._extract_available_evidence(session)
        evidence_metadata = self._extract_evidence_metadata(session)
        missing_required_evidence = self._extract_missing_required_evidence(session)

        session.set_status(InvestigationStatus.UNDERSTANDING)
        session.add_reasoning_step({
            "stage": "understand",
            "summary": "Built initial engineering context from observations.",
            "data": {
                "context_status": "initial",
                "available_evidence_count": len(available_evidence),
                "evidence_metadata_count": len(evidence_metadata),
                "has_missing_required_evidence": bool(missing_required_evidence),
            },
        })

        session.set_status(InvestigationStatus.VALIDATING)

        if missing_required_evidence:
            validation_summary = "Available data is insufficient for a final engineering conclusion."
            data_quality = "insufficient_for_final_decision"
        else:
            validation_summary = "Required evidence is available for a preliminary engineering decision."
            data_quality = "sufficient_for_preliminary_decision"

        session.add_reasoning_step({
            "stage": "validate",
            "summary": validation_summary,
            "data": {
                "data_quality": data_quality,
                "available_evidence": available_evidence,
                "evidence_metadata": evidence_metadata,
                "missing_required_evidence": missing_required_evidence,
            },
        })

        session.set_status(InvestigationStatus.HYPOTHESIZING)

        self._ensure_default_hypotheses(session)

        ranked_hypotheses = self._rank_hypotheses(session.hypotheses)
        top_ranked_hypothesis = ranked_hypotheses[0] if ranked_hypotheses else None

        session.add_reasoning_step({
            "stage": "hypothesize",
            "summary": "Generated or accepted competing engineering hypotheses.",
            "data": {
                "hypothesis_count": len(session.hypotheses),
                "hypothesis_source": "engineering_role_knowledge",
                "top_ranked_hypothesis": top_ranked_hypothesis,
            },
        })

        top_hypothesis_missing_evidence = []
        if top_ranked_hypothesis:
            top_hypothesis_missing_evidence = top_ranked_hypothesis.get("missing_evidence", [])

        combined_missing_evidence = self._merge_unique(
            missing_required_evidence,
            top_hypothesis_missing_evidence,
        )

        unresolved_conflicts = self._extract_unresolved_conflicts(ranked_hypotheses)
        blocking_conflicts = self._extract_blocking_conflicts(unresolved_conflicts)

        evidence_quality = score_evidence_quality(
            available_evidence=available_evidence,
            missing_required_evidence=combined_missing_evidence,
            unresolved_conflicts=unresolved_conflicts,
            evidence_metadata=evidence_metadata,
        )

        final_conclusion_allowed = not bool(
            combined_missing_evidence or blocking_conflicts
        )

        session.set_status(InvestigationStatus.REASONING)
        session.add_reasoning_step({
            "stage": "reason",
            "summary": "Applied preliminary engineering reasoning using evidence sufficiency, hypothesis evaluations, evidence conflicts, and metadata-aware evidence quality.",
            "data": {
                "reasoning_mode": "hypothesis_aware_conflict_aware_metadata_quality_aware_preliminary_reasoning",
                "final_conclusion_allowed": final_conclusion_allowed,
                "top_ranked_hypothesis": top_ranked_hypothesis,
                "combined_missing_evidence": combined_missing_evidence,
                "unresolved_conflicts": unresolved_conflicts,
                "blocking_conflicts": blocking_conflicts,
                "conflict_blocking": bool(blocking_conflicts),
                "evidence_quality": evidence_quality,
            },
        })

        session.set_status(InvestigationStatus.EVALUATING)

        if not final_conclusion_allowed:
            evaluation_confidence = "low"
            if unresolved_conflicts and combined_missing_evidence:
                evaluation_risk = "high_due_to_missing_critical_evidence_and_unresolved_conflicts"
            elif unresolved_conflicts:
                evaluation_risk = "high_due_to_unresolved_evidence_conflicts"
            else:
                evaluation_risk = "high_due_to_missing_critical_evidence"
        elif top_ranked_hypothesis:
            evaluation_confidence = top_ranked_hypothesis.get("confidence", "low")
            evaluation_risk = top_ranked_hypothesis.get("risk", "medium")
        else:
            evaluation_confidence = "low"
            evaluation_risk = "unknown"

        session.add_reasoning_step({
            "stage": "evaluate",
            "summary": "Evaluated confidence, risk, missing evidence, evidence conflicts, metadata-aware evidence quality, and ranked hypotheses.",
            "data": {
                "confidence": evaluation_confidence,
                "risk": evaluation_risk,
                "missing_data": combined_missing_evidence,
                "unresolved_conflicts": unresolved_conflicts,
                "blocking_conflicts": blocking_conflicts,
                "conflict_blocking": bool(blocking_conflicts),
                "evidence_quality": evidence_quality,
                "ranked_hypotheses": ranked_hypotheses,
            },
        })

        session.set_status(InvestigationStatus.DECIDING)

        if combined_missing_evidence or blocking_conflicts:
            session.add_decision({
                "decision_type": "evidence_required_before_final_decision",
                "decision": "Do not issue a final root-cause conclusion. Required evidence must be collected and evidence conflicts must be resolved before re-energization or final RCA.",
                "confidence": "low",
                "safety_position": "conservative",
                "top_ranked_hypothesis": top_ranked_hypothesis,
                "required_next_evidence": combined_missing_evidence,
                "unresolved_conflicts": unresolved_conflicts,
                "blocking_conflicts": blocking_conflicts,
                "conflict_blocking": bool(blocking_conflicts),
                "evidence_quality": evidence_quality,
                "re_energization_readiness": "not_evaluated",
            })
        else:
            session.add_decision({
                "decision_type": "engineering_recommendation",
                "decision": "A preliminary engineering recommendation can be issued based on the available evidence, current hypothesis ranking, and metadata-aware evidence quality.",
                "confidence": evaluation_confidence,
                "safety_position": "controlled",
                "top_ranked_hypothesis": top_ranked_hypothesis,
                "required_next_evidence": [],
                "unresolved_conflicts": [],
                "conflict_blocking": False,
                "evidence_quality": evidence_quality,
                "re_energization_readiness": "not_evaluated",
            })

        session.add_reasoning_step({
            "stage": "decide",
            "summary": "Produced an engineering decision using evidence sufficiency, hypothesis ranking, conflict blocking, and metadata-aware evidence quality.",
            "data": {
                "decision_count": len(session.decisions),
                "decision_type": session.decisions[-1]["decision_type"] if session.decisions else None,
                "top_ranked_hypothesis": top_ranked_hypothesis,
                "unresolved_conflicts": unresolved_conflicts,
                "blocking_conflicts": blocking_conflicts,
                "conflict_blocking": bool(blocking_conflicts),
                "evidence_quality": evidence_quality,
            },
        })

        session.set_status(InvestigationStatus.EXPLAINING)

        if combined_missing_evidence or blocking_conflicts:
            report_summary = (
                "The investigation cannot reach a final root-cause conclusion because "
                "required evidence is missing or evidence conflicts remain unresolved. "
                "The safest engineering position is to keep the transformer out of service "
                "until the missing evidence is reviewed and conflicts are resolved."
            )
            report_confidence = "low"
        else:
            report_summary = (
                "The investigation has sufficient evidence for a preliminary engineering recommendation. "
                "The recommendation remains subject to metadata-aware evidence quality, normal engineering review, "
                "and operational approval."
            )
            report_confidence = evaluation_confidence

        session.add_report({
            "title": "Preliminary Transformer Differential Trip Investigation",
            "summary": report_summary,
            "confidence": report_confidence,
            "top_ranked_hypothesis": top_ranked_hypothesis,
            "ranked_hypotheses": ranked_hypotheses,
            "next_required_evidence": combined_missing_evidence,
            "unresolved_conflicts": unresolved_conflicts,
                "blocking_conflicts": blocking_conflicts,
                "conflict_blocking": bool(blocking_conflicts),
            "evidence_quality": evidence_quality,
                "re_energization_readiness": "not_evaluated",
            })

        session.add_reasoning_step({
            "stage": "explain",
            "summary": "Generated an auditable preliminary engineering explanation with hypothesis ranking, conflict status, and metadata-aware evidence quality.",
            "data": {
                "report_count": len(session.reports),
            },
        })

        session.set_status(InvestigationStatus.LEARNING)
        session.add_reasoning_step({
            "stage": "learn",
            "summary": "Prepared the investigation for future engineering memory storage.",
            "data": {
                "learning_status": "pending_case_outcome",
            },
        })

        session.set_status(InvestigationStatus.COMPLETED)

        return session

    def _extract_evidence_metadata(self, session: EngineeringSession) -> list[dict]:
        metadata: list[dict] = []

        for observation in session.observations:
            for item in observation.get("evidence_metadata", []):
                if item not in metadata:
                    metadata.append(item)

        return metadata

    def _extract_available_evidence(self, session: EngineeringSession) -> list[str]:
        available: list[str] = []

        for observation in session.observations:
            for item in observation.get("available_evidence", []):
                if item not in available:
                    available.append(item)

        return available

    def _extract_missing_required_evidence(self, session: EngineeringSession) -> list[str]:
        missing: list[str] = []

        for observation in session.observations:
            for item in observation.get("missing_required_evidence", []):
                if item not in missing:
                    missing.append(item)

        return missing

    def _extract_unresolved_conflicts(self, hypotheses: list[dict]) -> list[dict]:
        unresolved_conflicts: list[dict] = []

        for hypothesis in hypotheses:
            for conflict in hypothesis.get("conflicts", []):
                if conflict not in unresolved_conflicts:
                    unresolved_conflicts.append(conflict)

        return unresolved_conflicts

    def _extract_blocking_conflicts(self, conflicts: list[dict]) -> list[dict]:
        blocking_severities = {"medium", "high", "critical"}

        return [
            conflict
            for conflict in conflicts
            if conflict.get("severity", "medium") in blocking_severities
        ]
    def _ensure_default_hypotheses(self, session: EngineeringSession) -> None:
        if session.hypotheses:
            return

        session.add_hypothesis({
            "hypothesis": "Insufficient evidence to determine root cause",
            "confidence": "low",
            "supporting_evidence": [],
            "missing_evidence": self._extract_missing_required_evidence(session),
            "conflicts": [],
            "risk": "high",
            "recommended_next_action": "Collect missing evidence before issuing any final engineering conclusion.",
            "source": "EngineeringBrain default hypothesis",
        })

        session.add_hypothesis({
            "hypothesis": "Protection or asset event requires further engineering review",
            "confidence": "low",
            "supporting_evidence": [],
            "missing_evidence": self._extract_missing_required_evidence(session),
            "conflicts": [],
            "risk": "medium",
            "recommended_next_action": "Review protection records, asset condition, and operational context.",
            "source": "EngineeringBrain default hypothesis",
        })

    def _rank_hypotheses(self, hypotheses: list[dict]) -> list[dict]:
        return sorted(
            hypotheses,
            key=lambda hypothesis: (
                self.CONFIDENCE_RANK.get(hypothesis.get("confidence", "low"), 0),
                len(hypothesis.get("supporting_evidence", [])),
                -len(hypothesis.get("missing_evidence", [])),
                -len(hypothesis.get("conflicts", [])),
            ),
            reverse=True,
        )

    def _merge_unique(self, first: list[str], second: list[str]) -> list[str]:
        merged: list[str] = []

        for item in first + second:
            if item not in merged:
                merged.append(item)

        return merged



