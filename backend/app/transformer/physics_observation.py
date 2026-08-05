from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class PhysicsObservation(BaseModel):
    """
    Auditable shadow observation produced by the
    transformer physics layer.

    This observation does not modify confidence,
    ranking, readiness, safety state, or decisions.
    """

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
    )

    observation_type: str = Field(min_length=1)
    source: str = "transformer_physics"

    data: dict[str, Any] = Field(
        default_factory=dict
    )

    provenance: dict[str, Any] = Field(
        default_factory=dict
    )

    validity_status: str = "unknown"

    affects_confidence: bool = False
    affects_ranking: bool = False
    affects_decision: bool = False
