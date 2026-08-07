from __future__ import annotations

from app.thinking.engine import (
    EngineeringThinkingEngine,
)
from app.thinking.processors.decide import (
    DecideProcessor,
)
from app.thinking.processors.explain import (
    ExplainProcessor,
)
from app.thinking.processors.hypothesize import (
    HypothesizeProcessor,
)
from app.thinking.processors.learn import (
    LearnProcessor,
)
from app.thinking.processors.observe import (
    ObserveProcessor,
)
from app.thinking.processors.rank_evidence import (
    RankEvidenceProcessor,
)
from app.thinking.processors.resolve_conflicts import (
    ResolveConflictsProcessor,
)
from app.thinking.processors.safety_gate import (
    SafetyGateProcessor,
)
from app.thinking.processors.understand import (
    UnderstandProcessor,
)
from app.thinking.processors.validate import (
    ValidateProcessor,
)
from app.thinking.processors.verify_physics import (
    VerifyPhysicsProcessor,
)


def build_default_thinking_engine(
) -> EngineeringThinkingEngine:
    return EngineeringThinkingEngine(
        processors=(
            ObserveProcessor(),
            UnderstandProcessor(),
            ValidateProcessor(),
            HypothesizeProcessor(),
            RankEvidenceProcessor(),
            ResolveConflictsProcessor(),
            VerifyPhysicsProcessor(),
            SafetyGateProcessor(),
            DecideProcessor(),
            ExplainProcessor(),
            LearnProcessor(),
        )
    )