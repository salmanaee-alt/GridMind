from __future__ import annotations

from typing import Protocol

from app.thinking.contracts import (
    ThinkingStage,
    ThinkingState,
)


class ThinkingStageProcessor(Protocol):
    stage: ThinkingStage

    def execute(
        self,
        state: ThinkingState,
    ) -> ThinkingState:
        ...