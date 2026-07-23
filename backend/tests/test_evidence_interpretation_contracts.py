import pytest
from pydantic import ValidationError

from app.capabilities.evidence_interpretation.contracts import (
    EvidenceInterpretationItem,
    EvidenceInterpretationRequest,
    EvidenceInterpretationResult,
)


def test_valid_evidence_interpretation_request() -> None:
    request = EvidenceInterpretationRequest(
        domain="transformer",
        asset_type="power_transformer",
        available_evidence=(
            "Buchholz alarm",
            "DGA report",
        ),
        missing_evidence=(
            "COMTRADE waveform",
        ),
        investigation_stage="initial",
    )

    assert request.domain == "transformer"
    assert len(request.available_evidence) == 2


def test_request_normalizes_strings() -> None:
    request = EvidenceInterpretationRequest(
        domain=" transformer ",
        asset_type=" power_transformer ",
        available_evidence=(
            " DGA report ",
        ),
        investigation_stage=" initial ",
    )

    assert request.domain == "transformer"
    assert request.asset_type == "power_transformer"
    assert request.available_evidence == (
        "DGA report",
    )
    assert request.investigation_stage == "initial"


def test_request_rejects_duplicate_evidence() -> None:
    with pytest.raises(ValidationError):
        EvidenceInterpretationRequest(
            domain="transformer",
            asset_type="power_transformer",
            available_evidence=(
                "DGA report",
                "DGA report",
            ),
            investigation_stage="initial",
        )


def test_request_rejects_available_missing_overlap() -> None:
    with pytest.raises(ValidationError):
        EvidenceInterpretationRequest(
            domain="transformer",
            asset_type="power_transformer",
            available_evidence=(
                "DGA report",
            ),
            missing_evidence=(
                "DGA report",
            ),
            investigation_stage="initial",
        )


def test_valid_evidence_interpretation_result() -> None:
    result = EvidenceInterpretationResult(
        interpretations=(
            EvidenceInterpretationItem(
                evidence="Buchholz alarm",
                interpretation=(
                    "Gas accumulation or oil movement "
                    "was detected."
                ),
                engineering_significance=(
                    "Requires correlation with other "
                    "transformer condition evidence."
                ),
            ),
        ),
        unresolved_evidence=(
            "Unknown relay flag",
        ),
    )

    assert len(result.interpretations) == 1
    assert result.unresolved_evidence == (
        "Unknown relay flag",
    )


def test_result_rejects_duplicate_interpreted_evidence() -> None:
    with pytest.raises(ValidationError):
        EvidenceInterpretationResult(
            interpretations=(
                EvidenceInterpretationItem(
                    evidence="DGA report",
                    interpretation="First interpretation",
                    engineering_significance="First significance",
                ),
                EvidenceInterpretationItem(
                    evidence="DGA report",
                    interpretation="Second interpretation",
                    engineering_significance="Second significance",
                ),
            ),
        )


def test_result_rejects_interpreted_unresolved_overlap() -> None:
    with pytest.raises(ValidationError):
        EvidenceInterpretationResult(
            interpretations=(
                EvidenceInterpretationItem(
                    evidence="DGA report",
                    interpretation="Interpretation",
                    engineering_significance="Significance",
                ),
            ),
            unresolved_evidence=(
                "DGA report",
            ),
        )


def test_contracts_reject_extra_fields() -> None:
    with pytest.raises(ValidationError):
        EvidenceInterpretationRequest(
            domain="transformer",
            asset_type="power_transformer",
            investigation_stage="initial",
            unexpected=True,
        )
        