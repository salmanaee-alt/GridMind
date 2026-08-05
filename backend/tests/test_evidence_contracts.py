from app.brain.evidence_contracts import (
    EngineeringEvidence,
    EvidenceCategory,
    EvidenceValidity,
)

import pytest
from pydantic import ValidationError


def test_can_create_engineering_evidence():
    evidence = EngineeringEvidence(
        evidence_id="EV-001",
        evidence_type="differential_current",
        category=EvidenceCategory.PHYSICS,
        source="transformer_physics",
        value=5.2,
        unit="A",
    )

    assert evidence.evidence_id == "EV-001"
    assert evidence.category == EvidenceCategory.PHYSICS
    assert evidence.validity == EvidenceValidity.UNKNOWN
    assert evidence.affects_reasoning is False


def test_accepts_provenance():
    evidence = EngineeringEvidence(
        evidence_id="EV-002",
        evidence_type="harmonic",
        category=EvidenceCategory.PHYSICS,
        source="physics",
        provenance={
            "algorithm": "v0.39",
            "inputs": ["hv", "lv"],
        },
    )

    assert evidence.provenance["algorithm"] == "v0.39"


def test_accepts_metadata():
    evidence = EngineeringEvidence(
        evidence_id="EV-003",
        evidence_type="relay_target",
        category=EvidenceCategory.PROTECTION,
        source="relay",
        metadata={
            "relay_model": "SEL-487E",
        },
    )

    assert evidence.metadata["relay_model"] == "SEL-487E"


def test_rejects_confidence_above_one():
    with pytest.raises(ValidationError):
        EngineeringEvidence(
            evidence_id="EV-004",
            evidence_type="physics",
            category=EvidenceCategory.PHYSICS,
            source="physics",
            confidence=1.1,
        )


def test_rejects_confidence_below_zero():
    with pytest.raises(ValidationError):
        EngineeringEvidence(
            evidence_id="EV-005",
            evidence_type="physics",
            category=EvidenceCategory.PHYSICS,
            source="physics",
            confidence=-0.1,
        )


def test_evidence_validity_enum():
    evidence = EngineeringEvidence(
        evidence_id="EV-006",
        evidence_type="measurement",
        category=EvidenceCategory.MEASUREMENT,
        source="meter",
        validity=EvidenceValidity.VALID,
    )

    assert evidence.validity == EvidenceValidity.VALID


def test_affects_reasoning_defaults_false():
    evidence = EngineeringEvidence(
        evidence_id="EV-007",
        evidence_type="inspection",
        category=EvidenceCategory.INSPECTION,
        source="field",
    )

    assert evidence.affects_reasoning is False
    