from __future__ import annotations

from typing import Literal

from app.transformer.physics_contracts import (
    CTRatio,
    DifferentialCurrentResult,
    ThreePhaseCurrentMeasurement,
    TransformerDifferentialPhysicsContext,
    DifferentialCharacteristicEvaluation,
    DifferentialCharacteristicSettings,
    HarmonicCurrentMeasurement,
    HarmonicRestraintEvaluation,
    HarmonicRestraintSettings,
    HarmonicPhysicsValidity,
    DifferentialOperatingRegionSummary,
)


def normalize_current_to_ct_secondary(
    *,
    currents: ThreePhaseCurrentMeasurement,
    ct_ratio: CTRatio,
) -> ThreePhaseCurrentMeasurement:
    """
    Convert primary current magnitudes to equivalent
    CT secondary current magnitudes.

    Audit/physics foundation only.
    No protection or engineering decision is produced.
    """

    ratio = ct_ratio.ratio

    return ThreePhaseCurrentMeasurement(
        phase_a=currents.phase_a / ratio,
        phase_b=currents.phase_b / ratio,
        phase_c=currents.phase_c / ratio,
        unit=currents.unit,
    )


def refer_current_to_voltage_side(
    *,
    currents: ThreePhaseCurrentMeasurement,
    from_voltage_kv: float,
    to_voltage_kv: float,
) -> ThreePhaseCurrentMeasurement:
    """
    Refer three-phase current magnitudes from one
    transformer voltage side to another using the
    ideal transformer current ratio.

    I_to = I_from * V_from / V_to

    Magnitude-only physics foundation.
    No vector-group or phase-angle compensation is applied.
    No protection decision is produced.
    """

    if from_voltage_kv <= 0.0:
        raise ValueError(
            "from_voltage_kv must be greater than zero."
        )

    if to_voltage_kv <= 0.0:
        raise ValueError(
            "to_voltage_kv must be greater than zero."
        )

    scale = from_voltage_kv / to_voltage_kv

    return ThreePhaseCurrentMeasurement(
        phase_a=currents.phase_a * scale,
        phase_b=currents.phase_b * scale,
        phase_c=currents.phase_c * scale,
        unit=currents.unit,
    )


def differential_currents_are_comparable(
    *,
    context: TransformerDifferentialPhysicsContext,
) -> bool:
    """
    Return whether HV/LV current quantities may be treated
    as physically comparable for differential calculations.

    This is a physics safety gate only.
    It does not calculate Idiff and does not affect
    engineering decisions.
    """

    return (
        context.vector_group != "unknown"
        and context.vector_group_compensation_applied
    )


def calculate_differential_and_restraint_currents(
    *,
    hv_currents: ThreePhaseCurrentMeasurement,
    lv_currents_referred_to_hv: ThreePhaseCurrentMeasurement,
    context: TransformerDifferentialPhysicsContext,
) -> DifferentialCurrentResult:
    """
    Calculate simple magnitude-based differential
    and restraint currents after comparability is confirmed.

    Idiff = abs(Ihv - Ilv_referred)

    Irestraint = (abs(Ihv) + abs(Ilv_referred)) / 2

    Shadow-only physics calculation.
    No relay trip decision is produced.
    """

    if not differential_currents_are_comparable(
        context=context
    ):
        raise ValueError(
            "Differential currents are not physically "
            "comparable until vector-group compensation "
            "is known and applied."
        )

    return DifferentialCurrentResult(
        phase_a_diff_a=abs(
            hv_currents.phase_a
            - lv_currents_referred_to_hv.phase_a
        ),
        phase_b_diff_a=abs(
            hv_currents.phase_b
            - lv_currents_referred_to_hv.phase_b
        ),
        phase_c_diff_a=abs(
            hv_currents.phase_c
            - lv_currents_referred_to_hv.phase_c
        ),
        phase_a_restraint_a=(
            abs(hv_currents.phase_a)
            + abs(lv_currents_referred_to_hv.phase_a)
        ) / 2,
        phase_b_restraint_a=(
            abs(hv_currents.phase_b)
            + abs(lv_currents_referred_to_hv.phase_b)
        ) / 2,
        phase_c_restraint_a=(
            abs(hv_currents.phase_c)
            + abs(lv_currents_referred_to_hv.phase_c)
        ) / 2,
        affects_decision=False,
    )


def evaluate_differential_characteristic(
    *,
    currents: DifferentialCurrentResult,
    settings: DifferentialCharacteristicSettings,
) -> DifferentialCharacteristicEvaluation:
    """
    Evaluate a simple single-slope percentage differential
    characteristic.

    operate threshold = pickup + slope * restraint

    Shadow-only physics evaluation.
    No protection or engineering decision is produced.
    """

    phase_a_threshold = (
        settings.pickup_a
        + settings.slope * currents.phase_a_restraint_a
    )

    phase_b_threshold = (
        settings.pickup_a
        + settings.slope * currents.phase_b_restraint_a
    )

    phase_c_threshold = (
        settings.pickup_a
        + settings.slope * currents.phase_c_restraint_a
    )

    return DifferentialCharacteristicEvaluation(
        phase_a_operate=(
            currents.phase_a_diff_a
            >= phase_a_threshold
        ),
        phase_b_operate=(
            currents.phase_b_diff_a
            >= phase_b_threshold
        ),
        phase_c_operate=(
            currents.phase_c_diff_a
            >= phase_c_threshold
        ),
        phase_a_threshold_a=phase_a_threshold,
        phase_b_threshold_a=phase_b_threshold,
        phase_c_threshold_a=phase_c_threshold,
        affects_decision=False,
    )


def summarize_differential_operating_region(
    evaluation: DifferentialCharacteristicEvaluation,
) -> DifferentialOperatingRegionSummary:
    operating_phases: list[
        Literal["A", "B", "C"]
    ] = []

    if evaluation.phase_a_operate:
        operating_phases.append("A")

    if evaluation.phase_b_operate:
        operating_phases.append("B")

    if evaluation.phase_c_operate:
        operating_phases.append("C")

    return DifferentialOperatingRegionSummary(
        any_phase_operate=bool(
            operating_phases
        ),
        operating_phases=tuple(
            operating_phases
        ),
    )


def calculate_harmonic_ratios(
    *,
    measurement: HarmonicCurrentMeasurement,
) -> dict[str, float | None | bool]:
    """
    Calculate harmonic current ratios relative to
    the fundamental component.

    H2% = I2 / I1 * 100
    H5% = I5 / I1 * 100

    If the fundamental current is zero, ratios are
    undefined and returned as None.

    Shadow-only physics calculation.
    """

    if measurement.fundamental_a == 0.0:
        return {
            "second_harmonic_percent": None,
            "fifth_harmonic_percent": None,
            "ratios_defined": False,
            "affects_decision": False,
        }

    return {
        "second_harmonic_percent": round(
            measurement.second_harmonic_a
            / measurement.fundamental_a
            * 100.0,
            4,
        ),
        "fifth_harmonic_percent": round(
            measurement.fifth_harmonic_a
            / measurement.fundamental_a
            * 100.0,
            4,
        ),
        "ratios_defined": True,
        "affects_decision": False,
    }


def evaluate_harmonic_restraint(
    *,
    measurement: HarmonicCurrentMeasurement,
    settings: HarmonicRestraintSettings,
) -> HarmonicRestraintEvaluation:
    """
    Evaluate harmonic restraint indicators from
    harmonic-current ratios.

    Shadow-only physics evaluation.
    No relay or engineering decision is produced.
    """

    ratios = calculate_harmonic_ratios(
        measurement=measurement
    )

    if not ratios["ratios_defined"]:
        return HarmonicRestraintEvaluation(
            second_harmonic_restraint=False,
            fifth_harmonic_restraint=False,
            any_harmonic_restraint=False,
            ratios_defined=False,
            affects_decision=False,
        )

    second_harmonic_restraint = (
        ratios["second_harmonic_percent"]
        >= settings.second_harmonic_threshold_percent
    )

    fifth_harmonic_restraint = (
        ratios["fifth_harmonic_percent"]
        >= settings.fifth_harmonic_threshold_percent
    )

    return HarmonicRestraintEvaluation(
        second_harmonic_restraint=(
            second_harmonic_restraint
        ),
        fifth_harmonic_restraint=(
            fifth_harmonic_restraint
        ),
        any_harmonic_restraint=(
            second_harmonic_restraint
            or fifth_harmonic_restraint
        ),
        ratios_defined=True,
        affects_decision=False,
    )


def evaluate_harmonic_physics_validity(
    *,
    measurement: HarmonicCurrentMeasurement | None,
) -> HarmonicPhysicsValidity:
    """
    Evaluate whether harmonic-ratio physics is usable.

    Shadow-only validity assessment.
    No inrush, overexcitation, relay, or engineering
    conclusion is produced.
    """

    if measurement is None:
        return HarmonicPhysicsValidity(
            status="unavailable",
            reason="No harmonic current measurement is available.",
            affects_decision=False,
        )

    if measurement.fundamental_a == 0.0:
        return HarmonicPhysicsValidity(
            status="indeterminate",
            reason=(
                "Fundamental current is zero, so harmonic "
                "ratios cannot be physically defined."
            ),
            affects_decision=False,
        )

    return HarmonicPhysicsValidity(
        status="valid",
        reason=(
            "Fundamental current is available and harmonic "
            "ratios can be evaluated."
        ),
        affects_decision=False,
    )