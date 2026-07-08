from __future__ import annotations


def normalize_text(value: str | None) -> str:
    if value is None:
        return ""

    return value.strip().lower()


def evaluate_differential_trip_hypotheses(
    available_evidence: list[str],
    missing_required_evidence: list[str],
    buchholz_alarm: bool | None,
    comtrade_available: bool,
    dga_available: bool,
    oil_temperature_c: float | None,
    load_percent: float | None,
    relay_targets: list[str] | None = None,
    dga_status: str | None = None,
    comtrade_summary: str | None = None,
) -> list[dict]:
    relay_targets_text = " ".join(relay_targets or []).lower()
    dga_status_text = normalize_text(dga_status)
    comtrade_text = normalize_text(comtrade_summary)

    dga_abnormal = dga_status_text in [
        "abnormal",
        "critical",
        "alarm",
        "high_gas",
        "fault_gas_detected",
    ]
    dga_normal = dga_status_text == "normal"

    inrush_detected = comtrade_text == "inrush_detected"
    no_inrush_detected = comtrade_text == "no_inrush"
    ct_saturation_detected = comtrade_text == "ct_saturation"
    ct_circuit_issue_detected = comtrade_text == "ct_circuit_issue"

    differential_operated = (
        "87t" in relay_targets_text
        or "differential" in relay_targets_text
    )

    conflicts: list[dict] = []

    if dga_normal and differential_operated and no_inrush_detected:
        conflicts.append({
            "conflict": "Differential operation with no inrush indication, but DGA status is normal.",
            "severity": "medium",
            "recommended_verification": "Verify DGA sampling time, relay targets, COMTRADE waveform, and visual inspection before increasing internal fault confidence.",
        })

    if dga_abnormal and inrush_detected:
        conflicts.append({
            "conflict": "DGA is abnormal, but COMTRADE indicates inrush.",
            "severity": "medium",
            "recommended_verification": "Confirm whether the event occurred during energization and review harmonic restraint operation.",
        })

    evaluations: list[dict] = []

    internal_supporting: list[str] = []

    if differential_operated:
        internal_supporting.append("Differential relay target indicates transformer differential operation.")

    if dga_abnormal:
        internal_supporting.append("DGA status is abnormal.")

    if buchholz_alarm is True:
        internal_supporting.append("Buchholz relay alarm is present.")

    if no_inrush_detected:
        internal_supporting.append("COMTRADE summary does not indicate inrush.")

    internal_missing = [
        item
        for item in [
            "DGA report",
            "Buchholz relay status",
            "Visual inspection",
            "COMTRADE waveform",
        ]
        if item in missing_required_evidence
    ]

    if dga_abnormal and differential_operated and no_inrush_detected:
        internal_confidence = "high"
    elif dga_abnormal or buchholz_alarm is True or (differential_operated and no_inrush_detected):
        internal_confidence = "medium"
    else:
        internal_confidence = "low"

    internal_conflicts = [
        conflict
        for conflict in conflicts
        if "DGA status is normal" in conflict["conflict"]
        or "DGA is abnormal" in conflict["conflict"]
    ]

    if internal_confidence == "high" and internal_conflicts:
        internal_confidence = "medium"

    evaluations.append({
        "hypothesis": "Internal transformer fault",
        "confidence": internal_confidence,
        "supporting_evidence": internal_supporting,
        "missing_evidence": internal_missing,
        "conflicts": internal_conflicts,
        "risk": "high",
        "recommended_next_action": "Review COMTRADE, DGA, Buchholz status, visual inspection, and any detected evidence conflicts before re-energization.",
    })

    external_supporting: list[str] = []

    if ct_saturation_detected:
        external_supporting.append("COMTRADE summary indicates CT saturation.")

    if "HV/LV breaker status" not in missing_required_evidence:
        external_supporting.append("Breaker status is available for external fault review.")

    external_missing = [
        item
        for item in [
            "COMTRADE waveform",
            "HV/LV breaker status",
        ]
        if item in missing_required_evidence
    ]

    external_confidence = "medium" if ct_saturation_detected else "low"

    evaluations.append({
        "hypothesis": "External fault with CT saturation",
        "confidence": external_confidence,
        "supporting_evidence": external_supporting,
        "missing_evidence": external_missing,
        "conflicts": [],
        "risk": "medium",
        "recommended_next_action": "Review through-fault records, CT saturation signs, breaker status, and upstream/downstream protection operation.",
    })

    protection_supporting: list[str] = []

    if "Relay event report" in available_evidence:
        protection_supporting.append("Relay event report is available for settings and logic review.")

    protection_missing = [
        item
        for item in [
            "Relay event report",
            "Recent maintenance history",
        ]
        if item in missing_required_evidence
    ]

    protection_confidence = "low"

    evaluations.append({
        "hypothesis": "Protection misoperation",
        "confidence": protection_confidence,
        "supporting_evidence": protection_supporting,
        "missing_evidence": protection_missing,
        "conflicts": [],
        "risk": "medium",
        "recommended_next_action": "Review relay settings, recent setting changes, test records, and event report sequence.",
    })

    ct_supporting: list[str] = []

    if ct_circuit_issue_detected:
        ct_supporting.append("COMTRADE summary indicates possible CT circuit issue.")

    ct_missing = [
        item
        for item in [
            "COMTRADE waveform",
            "Recent maintenance history",
        ]
        if item in missing_required_evidence
    ]

    ct_confidence = "medium" if ct_circuit_issue_detected else "low"

    evaluations.append({
        "hypothesis": "CT circuit issue",
        "confidence": ct_confidence,
        "supporting_evidence": ct_supporting,
        "missing_evidence": ct_missing,
        "conflicts": [],
        "risk": "medium",
        "recommended_next_action": "Inspect CT secondary circuits, terminal tightness, test links, polarity, and recent maintenance records.",
    })

    inrush_supporting: list[str] = []

    if inrush_detected:
        inrush_supporting.append("COMTRADE summary indicates inrush.")

    if load_percent is not None and load_percent <= 10:
        inrush_supporting.append("Low load before trip may indicate energization or abnormal switching condition.")

    inrush_missing = [
        item
        for item in [
            "COMTRADE waveform",
            "Load before trip",
        ]
        if item in missing_required_evidence
    ]

    if inrush_detected:
        inrush_confidence = "high"
    elif load_percent is not None and load_percent <= 10:
        inrush_confidence = "medium"
    else:
        inrush_confidence = "low"

    inrush_conflicts = [
        conflict
        for conflict in conflicts
        if "COMTRADE indicates inrush" in conflict["conflict"]
    ]

    evaluations.append({
        "hypothesis": "Inrush or abnormal energization condition",
        "confidence": inrush_confidence,
        "supporting_evidence": inrush_supporting,
        "missing_evidence": inrush_missing,
        "conflicts": inrush_conflicts,
        "risk": "medium",
        "recommended_next_action": "Review energization timing, harmonic restraint, residual flux possibility, and COMTRADE waveform.",
    })

    return evaluations
