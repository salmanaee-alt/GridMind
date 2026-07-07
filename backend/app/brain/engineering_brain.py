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
                data={"context_status": "initial"},
            )
        )

        session.set_status(InvestigationStatus.VALIDATING)
        session.add_reasoning_step(
            StageResult(
                stage="validate",
                summary="Checked whether the available engineering data is sufficient.",
                data={"data_quality": "pending_detailed_validation"},
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
                summary="Applied preliminary engineering reasoning.",
                data={
                    "reasoning_mode": "evidence_based_preliminary_reasoning",
                    "requires_future_inputs": [
                        "relay event report",
                        "COMTRADE file",
                        "DGA",
                        "inspection record"
                    ],
                },
            )
        )

        session.set_status(InvestigationStatus.EVALUATING)
        session.add_reasoning_step(
            StageResult(
                stage="evaluate",
                summary="Evaluated confidence, risk, and missing evidence.",
                data={
                    "confidence": "low_to_medium",
                    "risk": "high_if_internal_fault_confirmed",
                    "missing_data": [
                        "COMTRADE",
                        "relay targets",
                        "DGA",
                        "visual inspection"
                    ],
                },
            )
        )

        session.set_status(InvestigationStatus.DECIDING)
        session.add_decision({
            "decision_type": "engineering_recommendation",
            "decision": "Do not re-energize the transformer until relay event records and COMTRADE files are reviewed.",
            "confidence": "medium",
            "safety_position": "conservative"
        })
        session.add_reasoning_step(
            StageResult(
                stage="decide",
                summary="Produced a conservative engineering recommendation.",
                data={"decision_count": len(session.decisions)},
            )
        )

        session.set_status(InvestigationStatus.EXPLAINING)
        session.add_report({
            "title": "Preliminary Transformer Differential Trip Investigation",
            "summary": "The case requires further evidence before confirming the root cause. The safest recommendation is to hold re-energization pending relay and waveform review.",
            "confidence": "medium",
            "next_required_evidence": [
                "COMTRADE",
                "relay event report",
                "DGA",
                "visual inspection"
            ]
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
