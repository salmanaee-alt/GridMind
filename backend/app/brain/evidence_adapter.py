from __future__ import annotations

from app.brain.evidence_contracts import (
    EngineeringEvidence,
    EvidenceCategory,
    EvidenceValidity,
)
from app.transformer.physics_observation import (
    PhysicsObservation,
)


def physics_observation_to_evidence(
    observation: PhysicsObservation,
) -> EngineeringEvidence:
    validity_map = {
        "valid": EvidenceValidity.VALID,
        "invalid": EvidenceValidity.INVALID,
        "unknown": EvidenceValidity.UNKNOWN,
        "unavailable": EvidenceValidity.INSUFFICIENT,
        "indeterminate": EvidenceValidity.UNKNOWN,
    }

    return EngineeringEvidence(
        evidence_id=f"physics:{observation.observation_type}",
        evidence_type=observation.observation_type,
        category=EvidenceCategory.PHYSICS,
        source=observation.source,
        value=observation.data,
        validity=validity_map.get(
            observation.validity_status,
            EvidenceValidity.UNKNOWN,
        ),
        provenance=observation.provenance,
        affects_reasoning=False,
    )
