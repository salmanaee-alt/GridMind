import pytest
from pydantic import ValidationError

from app.capabilities.traceable_context.contracts import (
    TraceableEngineeringContextRequest,
    TraceableEngineeringContextResult,
    TraceableEvidenceItem,
)


def test_valid_traceable_context_request() -> None:
    request = TraceableEngineeringContextRequest(
        domain="transformer",
        asset_type="power_transformer",
        investigation_stage="initial",
        selected_knowledge_ids=(
            "EKO-0001",
            "EKO-0002",
        ),
        evidence_items=(
            TraceableEvidenceItem(
                evidence="DGA report",
                interpretation="DGA is available.",
                engineering_significance=(
                    "Provides transformer condition evidence."
                ),
                supporting_knowledge_ids=(
                    "EKO-0001",
                ),
            ),
        ),
        unresolved_evidence=(
            "Unknown diagnostic flag",
        ),
    )

    assert request.domain == "transformer"
    assert len(request.selected_knowledge_ids) == 2
    assert len(request.evidence_items) == 1


def test_request_normalizes_required_strings() -> None:
    request = TraceableEngineeringContextRequest(
        domain=" transformer ",
        asset_type=" power_transformer ",
        investigation_stage=" initial ",
    )

    assert request.domain == "transformer"
    assert request.asset_type == "power_transformer"
    assert request.investigation_stage == "initial"


def test_request_rejects_duplicate_knowledge_ids() -> None:
    with pytest.raises(ValidationError):
        TraceableEngineeringContextRequest(
            domain="transformer",
            asset_type="power_transformer",
            investigation_stage="initial",
            selected_knowledge_ids=(
                "EKO-0001",
                "EKO-0001",
            ),
        )


def test_request_rejects_duplicate_evidence_items() -> None:
    with pytest.raises(ValidationError):
        TraceableEngineeringContextRequest(
            domain="transformer",
            asset_type="power_transformer",
            investigation_stage="initial",
            evidence_items=(
                TraceableEvidenceItem(
                    evidence="DGA report",
                    interpretation="First",
                    engineering_significance="First",
                ),
                TraceableEvidenceItem(
                    evidence="DGA report",
                    interpretation="Second",
                    engineering_significance="Second",
                ),
            ),
        )


def test_request_rejects_interpreted_unresolved_overlap() -> None:
    with pytest.raises(ValidationError):
        TraceableEngineeringContextRequest(
            domain="transformer",
            asset_type="power_transformer",
            investigation_stage="initial",
            evidence_items=(
                TraceableEvidenceItem(
                    evidence="DGA report",
                    interpretation="Interpretation",
                    engineering_significance="Significance",
                ),
            ),
            unresolved_evidence=(
                "DGA report",
            ),
        )


def test_request_rejects_unselected_knowledge_reference() -> None:
    with pytest.raises(
        ValidationError,
        match="was not selected",
    ):
        TraceableEngineeringContextRequest(
            domain="transformer",
            asset_type="power_transformer",
            investigation_stage="initial",
            selected_knowledge_ids=(
                "EKO-0001",
            ),
            evidence_items=(
                TraceableEvidenceItem(
                    evidence="DGA report",
                    interpretation="Interpretation",
                    engineering_significance="Significance",
                    supporting_knowledge_ids=(
                        "EKO-9999",
                    ),
                ),
            ),
        )


def test_valid_traceable_context_result() -> None:
    result = TraceableEngineeringContextResult(
        knowledge_ids=(
            "EKO-0001",
        ),
        evidence_items=(
            TraceableEvidenceItem(
                evidence="DGA report",
                interpretation="Interpretation",
                engineering_significance="Significance",
                supporting_knowledge_ids=(
                    "EKO-0001",
                ),
            ),
        ),
        unresolved_evidence=(),
        traceability_complete=True,
        affects_decision=False,
    )

    assert result.traceability_complete is True
    assert result.affects_decision is False


def test_contracts_reject_extra_fields() -> None:
    with pytest.raises(ValidationError):
        TraceableEngineeringContextRequest(
            domain="transformer",
            asset_type="power_transformer",
            investigation_stage="initial",
            unexpected=True,
        )
        