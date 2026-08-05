from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class EvidenceCategory(str, Enum):
    PHYSICS = "physics"
    PROTECTION = "protection"
    MEASUREMENT = "measurement"
    SCADA = "scada"
    MAINTENANCE = "maintenance"
    INSPECTION = "inspection"
    DOCUMENT = "document"
    STANDARD = "standard"
    OPERATOR = "operator"
    AI_DERIVED = "ai_derived"


class EvidenceValidity(str, Enum):
    VALID = "valid"
    INVALID = "invalid"
    UNKNOWN = "unknown"
    INSUFFICIENT = "insufficient"


class EngineeringEvidence(BaseModel):
    """
    Canonical engineering evidence.

    All evidence entering the reasoning engine
    must be represented using this contract.
    """

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
    )

    evidence_id: str = Field(min_length=1)

    evidence_type: str = Field(min_length=1)

    category: EvidenceCategory

    source: str

    value: Any = None

    unit: str | None = None

    validity: EvidenceValidity = (
        EvidenceValidity.UNKNOWN
    )

    confidence: float = Field(
        ge=0.0,
        le=1.0,
        default=1.0,
    )

    provenance: dict[str, Any] = Field(
        default_factory=dict
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict
    )

    affects_reasoning: bool = False
    