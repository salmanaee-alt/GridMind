from __future__ import annotations

from app.thinking.contracts import (
    ThinkingStage,
    ThinkingState,
)


class ExplainProcessor:
    stage = ThinkingStage.EXPLAIN

    def execute(
        self,
        state: ThinkingState,
    ) -> ThinkingState:
        explanation_summary = {
            "observation_count": len(
                state.observations
            ),
            "evidence_count": len(
                state.evidence
            ),
            "hypothesis_count": len(
                state.hypotheses
            ),
            "physics_check_count": len(
                state.physics_checks
            ),
            "safety_finding_count": len(
                state.safety_findings
            ),
            "decision_count": len(
                state.decisions
            ),
        }

        explanation_available = any(
            explanation_summary.values()
        )

        explanation_item = {
            "type": "structured_engineering_summary",
            "summary": explanation_summary,
            "generated_by": "thinking_engine",
            "free_text_generated": False,
        }

        explanations = state.explanations

        if explanation_available:
            explanations = (
                *state.explanations,
                explanation_item,
            )

        return state.model_copy(
            update={
                "explanations": explanations,
                "metadata": {
                    **state.metadata,
                    "explain_stage": {
                        "explanation_available": (
                            explanation_available
                        ),
                        "explanation_count": len(
                            explanations
                        ),
                        "free_text_generated": False,
                    },
                },
            }
        )