from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import uuid4


class InvestigationStatus(str, Enum):
    CREATED = "created"
    OBSERVING = "observing"
    UNDERSTANDING = "understanding"
    VALIDATING = "validating"
    HYPOTHESIZING = "hypothesizing"
    REASONING = "reasoning"
    EVALUATING = "evaluating"
    DECIDING = "deciding"
    EXPLAINING = "explaining"
    LEARNING = "learning"
    COMPLETED = "completed"


@dataclass
class EngineeringSession:
    session_id: str = field(default_factory=lambda: str(uuid4()))
    title: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)

    status: InvestigationStatus = InvestigationStatus.CREATED

    observations: list[Any] = field(default_factory=list)
    evidence: list[Any] = field(default_factory=list)
    hypotheses: list[Any] = field(default_factory=list)
    reasoning_steps: list[Any] = field(default_factory=list)
    decisions: list[Any] = field(default_factory=list)
    reports: list[Any] = field(default_factory=list)

    metadata: dict[str, Any] = field(default_factory=dict)

    def set_status(self, status: InvestigationStatus) -> None:
        self.status = status

    def add_observation(self, observation: Any) -> None:
        self.observations.append(observation)

    def add_evidence(self, item: Any) -> None:
        self.evidence.append(item)

    def add_hypothesis(self, hypothesis: Any) -> None:
        self.hypotheses.append(hypothesis)

    def add_reasoning_step(self, step: Any) -> None:
        self.reasoning_steps.append(step)

    def add_decision(self, decision: Any) -> None:
        self.decisions.append(decision)

    def add_report(self, report: Any) -> None:
        self.reports.append(report)