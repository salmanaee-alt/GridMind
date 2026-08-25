from app.transformer.external_fault_discrimination import (
    evaluate_external_fault_discrimination,
)

from app.transformer.physics_contracts import (
    DifferentialOperatingRegionSummary,
)


def test_external_fault_discrimination_accepts_operating_region_summary():
    result = evaluate_external_fault_discrimination(
        operating_region=(
            DifferentialOperatingRegionSummary(
                any_phase_operate=True,
                operating_phases=("A",),
            )
        ),
        ct_saturation_status="supported",
    )

    assert result.status == "supported"
    assert result.confirmed is False


def test_no_operating_phase_is_insufficient_even_with_ct_saturation():
    result = evaluate_external_fault_discrimination(
        operating_region=(
            DifferentialOperatingRegionSummary(
                any_phase_operate=False,
                operating_phases=(),
            )
        ),
        ct_saturation_status="supported",
    )

    assert result.status == "insufficient_evidence"


def test_external_fault_with_ct_saturation_is_supported():
    result = evaluate_external_fault_discrimination(
        operating_region=(
            DifferentialOperatingRegionSummary(
                any_phase_operate=True,
                operating_phases=("A",),
            )
        ),
        ct_saturation_status="supported",
    )

    assert result.status == "supported"
    assert result.confirmed is False
    assert result.shadow_only is True
    assert result.affects_reasoning is False
    assert result.affects_decision is False


def test_operate_without_ct_saturation_is_not_enough():
    result = evaluate_external_fault_discrimination(
        operating_region=(
            DifferentialOperatingRegionSummary(
                any_phase_operate=True,
                operating_phases=("A",),
            )
        ),
        ct_saturation_status="not_supported",
    )

    assert result.status == "insufficient_evidence"
    assert result.confirmed is False


def test_ct_saturation_without_operate_is_not_enough():
    result = evaluate_external_fault_discrimination(
        operating_region=(
            DifferentialOperatingRegionSummary(
                any_phase_operate=False,
                operating_phases=(),
            )
        ),
        ct_saturation_status="supported",
    )

    assert result.status == "insufficient_evidence"
    assert result.confirmed is False


def test_missing_physics_is_insufficient():
    result = evaluate_external_fault_discrimination(
        operating_region=None,
        ct_saturation_status=None,
    )

    assert result.status == "insufficient_evidence"
    assert result.confirmed is False