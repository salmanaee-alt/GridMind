from __future__ import annotations

from app.brain.engineering_brain import EngineeringBrain
from app.brain.engineering_session import EngineeringSession
from app.transformer.knowledge import get_transformer_event_knowledge


class TransformerEngineer:
    def investigate_differential_trip(self) -> dict:
        knowledge = get_transformer_event_knowledge("differential_trip")

        session = EngineeringSession(
            title=knowledge["description"],
            metadata={
                "engineering_role": "Transformer Engineer",
                "event_type": "differential_trip",
                "risk_level": knowledge["risk_level"],
            },
        )

        session.add_observation({
            "event": "Transformer differential relay trip",
            "initial_safety_position": knowledge["initial_safety_position"],
            "required_evidence": knowledge["required_evidence"],
            "source": "Transformer Knowledge v0.1",
        })

        for hypothesis in knowledge["initial_hypotheses"]:
            session.add_hypothesis({
                "hypothesis": hypothesis,
                "status": "to_be_evaluated",
                "source": "Transformer Knowledge v0.1",
            })

        brain = EngineeringBrain()
        completed_session = brain.run(session)

        return {
            "role": "Transformer Engineer",
            "event_type": "differential_trip",
            "status": completed_session.status.value,
            "session": completed_session.to_dict(),
        }
