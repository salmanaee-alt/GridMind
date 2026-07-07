from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.brain.engineering_session import EngineeringSession, InvestigationStatus


@dataclass
class StageResult:
    stage: str
    summary: str
    data: dict[str, Any]


CONFIDENCE_RANK = {
    "low": 1,
    "medium": 2,
    "high": 3,
}


class EngineeringBrain:
    def run(self, session: EngineeringSession) -> EngineeringSession:
        if session.status == InvestigationStatus.COMPLETED:
            session.add_reasoning_step(
                StageResult(
                    stage="brain_guard",
                    summary="Session already completed. EngineeringBrain did not re-run the investigation.",
                    data={"guard": "completed_session"},
                )
            )
            return session

        missing_required_evidence = self._extract_missing_required_evidence(session)

        session.set_status(InvestigationStatus.OBSERVING)
        session.add_reasoning_step(
            StageResult(
                stage="observe",
                summary="Captured initial engineering observations.",
                data={"observation_count": len(session.observations)},
            )
        )

        session.set_status(InvestigationStatus.UNDERSTANDING)
        session.add_reasoning_step(
            StageResult(
                stage="understand",
                summary="Built initial engineering context from observations.",
                data={
                    "context_status": "initial",
                    "has_missing_required_evidence": bool(missing_required_evidence),
                },
            )
        )

        session.set_status(InvestigationStatus.VALIDATING)

        if missing_required_evidence:
            session.add_reasoning_step(
                StageResult(
                    stage="validate",
                    summary="Available data is insufficient for a final engineering conclusion.",
                    data={
                        "data_quality": "insufficient_for_final_decision",
                        "missing_required_evidence": missing_required_evidence,
                    },
                )
            )
        else:
            session.add_reasoning_step(
                StageResult(
                    stage="validate",
                    summary="Minimum required evidence appears available for preliminary reasoning.",
                    data={
                        "data_quality": "minimum_required_evidence_available",
                        "missing_required_evidence": [],
                    },
                )
            )

        session.set_status(InvestigationStatus.HYPOTHESIZING)

        if not session.hypotheses:
            session.add_hypothesis({
                "hypothesis": "Internal equipment fault",
                "confidence": "medium",
                "supporting_evidence": [],
                "missing_evidence": [],
                "risk": "high",
                "recommended_next_action": "Collect equipment-specific evidence before making a conclusion.",
                "source": "engineering_brain_default",
            })
            session.add_hypothesis({
                "hypothesis": "Protection misoperation",
                "confidence": "low",
                "supporting_evidence": [],
                "missing_evidence": [],
                "risk": "medium",
                "recommended_next_action": "Validate relay records and waveform data.",
                "source": "engineering_brain_default",
            })
            hypothesis_source = "engineering_brain_default"
        else:
            hypothesis_source = "engineering_role_knowledge"

        ranked_hypotheses = self._rank_hypotheses(session)
        top_ranked_hypothesis = ranked_hypotheses[0] if ranked_hypotheses else None
        hypothesis_missing_evidence = self._extract_hypothesis_missing_evidence(session)

        combined_missing_evidence = self._merge_unique(
            missing_required_evidence,
            hypothesis_missing_evidence,
        )

        session.add_reasoning_step(
            StageResult(
                stage="hypothesize",
                summary="Generated or accepted competing engineering hypotheses.",
                data={
                    "hypothesis_count": len(session.hypotheses),
                    "hypothesis_source": hypothesis_source,
                    "top_ranked_hypothesis": top_ranked_hypothesis,
                },
            )
        )

        session.set_status(InvestigationStatus.REASONING)
        session.add_reasoning_step(
            StageResult(
                stage="reason",
                summary="Applied preliminary engineering reasoning using evidence sufficiency and hypothesis evaluations.",
                data={
                    "reasoning_mode": "hypothesis_aware_preliminary_reasoning",
                    "final_conclusion_allowed": not bool(combined_missing_evidence),
                    "top_ranked_hypothesis": top_ranked_hypothesis,
                    "combined_missing_evidence": combined_missing_evidence,
                },
            )
        )

        session.set_status(InvestigationStatus.EVALUATING)

        if combined_missing_evidence:
            confidence = "low"
            risk = "high_due_to_missing_critical_evidence"
        elif top_ranked_hypothesis:
            confidence = top_ranked_hypothesis.get("confidence", "medium")
            risk = top_ranked_hypothesis.get("risk", "high_if_internal_fault_confirmed")
        else:
            confidence = "low"
            risk = "unknown"

        session.add_reasoning_step(
            StageResult(
                stage="evaluate",
                summary="Evaluated confidence, risk, missing evidence, and ranked hypotheses.",
                data={
                    "confidence": confidence,
                    "risk": risk,
                    "missing_data": combined_missing_evidence,
                    "ranked_hypotheses": ranked_hypotheses,
                },
            )
        )

        session.set_status(InvestigationStatus.DECIDING)

        if combined_missing_evidence:
            decision = {
                "decision_type": "evidence_required_before_final_decision",
                "decision": "Do not issue a final root-cause conclusion. Required evidence must be collected before re-energization or final RCA.",
                "confidence": "low",
                "safety_position": "conservative",
                "top_ranked_hypothesis": top_ranked_hypothesis,
                "required_next_evidence": combined_missing_evidence,
            }
        else:
            decision = {
                "decision_type": "engineering_recommendation",
                "decision": "Proceed with detailed engineering review. Available evidence is sufficient for preliminary analysis, but final energization decision remains subject to approved operational procedures.",
                "confidence": confidence,
                "safety_position": "controlled",
                "top_ranked_hypothesis": top_ranked_hypothesis,
            }

        session.add_decision(decision)

        session.add_reasoning_step(
            StageResult(
                stage="decide",
                summary="Produced an engineering decision using evidence sufficiency and hypothesis ranking.",
                data={
                    "decision_count": len(session.decisions),
                    "decision_type": decision["decision_type"],
                    "top_ranked_hypothesis": top_ranked_hypothesis,
                },
            )
        )

        session.set_status(InvestigationStatus.EXPLAINING)

        if combined_missing_evidence:
            report_summary = (
                "The investigation cannot reach a final root-cause conclusion because required evidence is missing. "
                "The safest engineering position is to keep the transformer out of service until the missing evidence is reviewed."
            )
            report_confidence = "low"
        else:
            report_summary = (
                "The minimum required evidence appears available for preliminary engineering reasoning. "
                "Further detailed review is still required before operational decisions."
            )
            report_confidence = confidence

        session.add_report({
            "title": "Preliminary Transformer Differential Trip Investigation",
            "summary": report_summary,
            "confidence": report_confidence,
            "top_ranked_hypothesis": top_ranked_hypothesis,
            "ranked_hypotheses": ranked_hypotheses,
            "next_required_evidence": combined_missing_evidence,
        })

        session.add_reasoning_step(
            StageResult(
                stage="explain",
                summary="Generated an auditable preliminary engineering explanation with hypothesis ranking.",
                data={"report_count": len(session.reports)},
            )
        )

        session.set_status(InvestigationStatus.LEARNING)
        session.add_reasoning_step(
            StageResult(
                stage="learn",
                summary="Prepared the investigation for future engineering memory storage.",
                data={"learning_status": "pending_case_outcome"},
            )
        )

        session.set_status(InvestigationStatus.COMPLETED)
        return session

    def _extract_missing_required_evidence(self, session: EngineeringSession) -> list[str]:
        missing: list[str] = []

        for observation in session.observations:
            if isinstance(observation, dict):
                observation_missing = observation.get("missing_required_evidence", [])

                if isinstance(observation_missing, list):
                    for item in observation_missing:
                        if isinstance(item, str) and item not in missing:
                            missing.append(item)

        return missing

    def _extract_hypothesis_missing_evidence(self, session: EngineeringSession) -> list[str]:
        missing: list[str] = []

        for hypothesis in session.hypotheses:
            if isinstance(hypothesis, dict):
                hypothesis_missing = hypothesis.get("missing_evidence", [])

                if isinstance(hypothesis_missing, list):
                    for item in hypothesis_missing:
                        if isinstance(item, str) and item not in missing:
                            missing.append(item)

        return missing

    def _rank_hypotheses(self, session: EngineeringSession) -> list[dict[str, Any]]:
        hypotheses = [
            hypothesis
            for hypothesis in session.hypotheses
            if isinstance(hypothesis, dict)
        ]

        return sorted(
            hypotheses,
            key=lambda hypothesis: (
                CONFIDENCE_RANK.get(str(hypothesis.get("confidence", "low")), 0),
                len(hypothesis.get("supporting_evidence", [])),
                -len(hypothesis.get("missing_evidence", [])),
            ),
            reverse=True,
        )

    def _merge_unique(self, first: list[str], second: list[str]) -> list[str]:
        merged: list[str] = []

        for item in first + second:
            if item not in merged:
                merged.append(item)

        return merged
