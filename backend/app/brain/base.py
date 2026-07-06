from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.brain.engineering_session import EngineeringSession


@dataclass
class StageResult:
    stage: str
    summary: str
    data: dict[str, Any]


class BrainStage:
    name: str = "base"

    def run(self, session: EngineeringSession) -> EngineeringSession:
        raise NotImplementedError
