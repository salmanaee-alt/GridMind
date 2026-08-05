from __future__ import annotations

from app.brain.evidence_graph_builder import (
    build_evidence_graph,
)
from app.brain.evidence_graph_validation import (
    validate_evidence_graph,
)

from dataclasses import asdict, dataclass, field, is_dataclass
from datetime import datetime, timezone
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
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    status: InvestigationStatus = InvestigationStatus.CREATED

    observations: list[Any] = field(default_factory=list)
    evidence: list[Any] = field(default_factory=list)
    evidence_graph: dict[str, Any] | None = None
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

    def set_evidence_graph(
        self,
        graph: dict[str, Any],
    ) -> None:
        self.evidence_graph = graph

    def add_hypothesis(self, hypothesis: Any) -> None:
        self.hypotheses.append(hypothesis)

    def add_reasoning_step(self, step: Any) -> None:
        self.reasoning_steps.append(step)

    def add_decision(self, decision: Any) -> None:
        self.decisions.append(decision)

    def add_report(self, report: Any) -> None:
        self.reports.append(report)

    def _serialize(self, value: Any) -> Any:
        if isinstance(value, Enum):
            return value.value
        if isinstance(value, datetime):
            return value.isoformat()
        if is_dataclass(value):
            return self._serialize(asdict(value))
        if isinstance(value, list):
            return [self._serialize(item) for item in value]
        if isinstance(value, dict):
            return {key: self._serialize(item) for key, item in value.items()}
        return value

    def to_dict(self) -> dict[str, Any]:
        return self._serialize({
            "session_id": self.session_id,
            "title": self.title,
            "created_at": self.created_at,
            "status": self.status,
            "observations": self.observations,
            "evidence": self.evidence,
            "evidence_graph": self.evidence_graph,
            "hypotheses": self.hypotheses,
            "reasoning_steps": self.reasoning_steps,
            "decisions": self.decisions,
            "reports": self.reports,
            "metadata": self.metadata,
        })
