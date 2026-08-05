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

class EvidenceRelationshipType(str, Enum):
    DERIVED_FROM = "derived_from"
    SUPPORTS = "supports"
    CONTRADICTS = "contradicts"
    VALIDATES = "validates"
    INVALIDATES = "invalidates"
    DEPENDS_ON = "depends_on"


class EvidenceRelationship(BaseModel):
    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
    )

    target_evidence_id: str = Field(
        min_length=1
    )

    relation: EvidenceRelationshipType

    source: str = Field(
        min_length=1
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict
    )

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

    relationships: tuple[
        EvidenceRelationship,
        ...
    ] = ()

    affects_reasoning: bool = False