from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.brain.engineering_session import EngineeringSession, InvestigationStatus


@dataclass
class StageResult:
    stage: str
    summary: str
    data: dict[str, Any]


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
                "initial_confidence": "medium",
                "reason": "A protective trip requires engineering investigation."
            })
            session.add_hypothesis({
                "hypothesis": "Protection misoperation",
                "initial_confidence": "low",
                "reason": "Protection operation must be validated using relay records and waveform data."
            })
            hypothesis_source = "engineering_brain_default"
        else:
            hypothesis_source = "engineering_role_knowledge"

        session.add_reasoning_step(
            StageResult(
                stage="hypothesize",
                summary="Generated or accepted competing engineering hypotheses.",
                data={
                    "hypothesis_count": len(session.hypotheses),
                    "hypothesis_source": hypothesis_source,
                },
            )
        )

        session.set_status(InvestigationStatus.REASONING)
        session.add_reasoning_step(
            StageResult(
                stage="reason",
                summary="Applied preliminary engineering reasoning based on current evidence.",
                data={
                    "reasoning_mode": "evidence_based_preliminary_reasoning",
                    "final_conclusion_allowed": not bool(missing_required_evidence),
                },
            )
        )

        session.set_status(InvestigationStatus.EVALUATING)

        if missing_required_evidence:
            confidence = "low"
            risk = "high_due_to_missing_critical_evidence"
        else:
            confidence = "medium"
            risk = "high_if_internal_fault_confirmed"

        session.add_reasoning_step(
            StageResult(
                stage="evaluate",
                summary="Evaluated confidence, risk, and missing evidence.",
                data={
                    "confidence": confidence,
                    "risk": risk,
                    "missing_data": missing_required_evidence,
                },
            )
        )

        session.set_status(InvestigationStatus.DECIDING)

        if missing_required_evidence:
            decision = {
                "decision_type": "evidence_required_before_final_decision",
                "decision": "Do not issue a final root-cause conclusion. Required evidence must be collected before re-energization or final RCA.",
                "confidence": "low",
                "safety_position": "conservative",
                "required_next_evidence": missing_required_evidence,
            }
        else:
            decision = {
                "decision_type": "engineering_recommendation",
                "decision": "Proceed with detailed engineering review. Available evidence is sufficient for preliminary analysis, but final energization decision remains subject to approved operational procedures.",
                "confidence": "medium",
                "safety_position": "controlled",
            }

        session.add_decision(decision)

        session.add_reasoning_step(
            StageResult(
                stage="decide",
                summary="Produced an engineering decision based on evidence sufficiency.",
                data={
                    "decision_count": len(session.decisions),
                    "decision_type": decision["decision_type"],
                },
            )
        )

        session.set_status(InvestigationStatus.EXPLAINING)

        if missing_required_evidence:
            report_summary = "The investigation cannot reach a final root-cause conclusion because required evidence is missing. The safest engineering position is to keep the transformer out of service until the missing evidence is reviewed."
            report_confidence = "low"
        else:
            report_summary = "The minimum required evidence appears available for preliminary engineering reasoning. Further detailed review is still required before operational decisions."
            report_confidence = "medium"

        session.add_report({
            "title": "Preliminary Transformer Differential Trip Investigation",
            "summary": report_summary,
            "confidence": report_confidence,
            "next_required_evidence": missing_required_evidence,
        })

        session.add_reasoning_step(
            StageResult(
                stage="explain",
                summary="Generated an auditable preliminary engineering explanation.",
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
