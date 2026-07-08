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
    available = set(available_evidence)
    missing = set(missing_required_evidence)

    relay_targets = relay_targets or []
    relay_targets_text = " ".join(relay_targets).lower()
    dga_status_text = normalize_text(dga_status)
    comtrade_text = normalize_text(comtrade_summary)

    dga_abnormal = dga_status_text in ["abnormal", "critical", "alarm", "high_gas", "fault_gas_detected"]
    dga_normal = dga_status_text == "normal"

    inrush_detected = comtrade_text == "inrush_detected"
    no_inrush_detected = comtrade_text == "no_inrush"

    differential_operated = (
        "87t" in relay_targets_text
        or "differential" in relay_targets_text
    )

    evaluations: list[dict] = []

    internal_supporting = []
    internal_missing = []

    if differential_operated:
        internal_supporting.append("Differential protection target indicates transformer differential operation")

    if "Differential relay targets" in available:
        internal_supporting.append("Differential relay targets available")

    if dga_abnormal:
        internal_supporting.append("DGA status is abnormal")

    if "DGA report" in available or dga_available:
        internal_supporting.append("DGA report available")

    if buchholz_alarm is True:
        internal_supporting.append("Buchholz alarm is active")

    if oil_temperature_c is not None and oil_temperature_c >= 90:
        internal_supporting.append("High oil temperature observed")

    if no_inrush_detected:
        internal_supporting.append("COMTRADE summary does not indicate inrush")

    for item in ["COMTRADE waveform", "DGA report", "Buchholz relay status", "Visual inspection"]:
        if item in missing:
            internal_missing.append(item)

    internal_confidence = "low"
    if dga_abnormal and differential_operated and no_inrush_detected:
        internal_confidence = "high"
    elif dga_abnormal or buchholz_alarm is True or (differential_operated and no_inrush_detected):
        internal_confidence = "medium"

    evaluations.append({
        "hypothesis": "Internal transformer fault",
        "confidence": internal_confidence,
        "supporting_evidence": internal_supporting,
        "missing_evidence": internal_missing,
        "risk": "high",
        "recommended_next_action": "Review COMTRADE, DGA, Buchholz status, and visual inspection before any re-energization.",
    })

    external_supporting = []
    external_missing = []

    if "HV/LV breaker status" in available:
        external_supporting.append("HV/LV breaker status available")

    if "COMTRADE waveform" in available or comtrade_available:
        external_supporting.append("COMTRADE waveform available")

    if comtrade_text == "ct_saturation":
        external_supporting.append("COMTRADE summary indicates possible CT saturation")

    for item in ["COMTRADE waveform", "HV/LV breaker status", "Differential relay targets"]:
        if item in missing:
            external_missing.append(item)

    external_confidence = "low"
    if comtrade_text == "ct_saturation":
        external_confidence = "medium"
    elif ("COMTRADE waveform" in available or comtrade_available) and "HV/LV breaker status" in available:
        external_confidence = "medium"

    evaluations.append({
        "hypothesis": "External fault with CT saturation",
        "confidence": external_confidence,
        "supporting_evidence": external_supporting,
        "missing_evidence": external_missing,
        "risk": "medium_to_high",
        "recommended_next_action": "Use COMTRADE and breaker status to distinguish internal fault from external through-fault with CT saturation.",
    })

    protection_supporting = []
    protection_missing = []

    if "Relay event report" in available:
        protection_supporting.append("Relay event report available")

    if dga_normal:
        protection_supporting.append("DGA status is normal")

    if inrush_detected:
        protection_supporting.append("COMTRADE summary indicates inrush, which may challenge differential protection logic")

    for item in ["Relay event report", "COMTRADE waveform", "Differential relay targets"]:
        if item in missing:
            protection_missing.append(item)

    protection_confidence = "low"
    if "Relay event report" in available and inrush_detected:
        protection_confidence = "medium"
    elif "Relay event report" in available and ("COMTRADE waveform" in available or comtrade_available):
        protection_confidence = "medium"

    evaluations.append({
        "hypothesis": "Protection misoperation",
        "confidence": protection_confidence,
        "supporting_evidence": protection_supporting,
        "missing_evidence": protection_missing,
        "risk": "medium",
        "recommended_next_action": "Validate relay settings, event report, and waveform alignment before concluding protection misoperation.",
    })

    ct_supporting = []
    ct_missing = []

    if "Differential relay targets" in available:
        ct_supporting.append("Differential relay targets available")

    if comtrade_text == "ct_circuit_issue":
        ct_supporting.append("COMTRADE summary suggests CT circuit issue")

    for item in ["COMTRADE waveform", "Differential relay targets"]:
        if item in missing:
            ct_missing.append(item)

    ct_confidence = "low"
    if comtrade_text == "ct_circuit_issue":
        ct_confidence = "medium"
    elif "Differential relay targets" in available and ("COMTRADE waveform" in available or comtrade_available):
        ct_confidence = "medium"

    evaluations.append({
        "hypothesis": "CT circuit issue",
        "confidence": ct_confidence,
        "supporting_evidence": ct_supporting,
        "missing_evidence": ct_missing,
        "risk": "medium_to_high",
        "recommended_next_action": "Check CT secondary circuit, polarity, wiring, saturation indicators, and relay current inputs.",
    })

    inrush_supporting = []
    inrush_missing = []

    if "COMTRADE waveform" in available or comtrade_available:
        inrush_supporting.append("COMTRADE waveform available")

    if inrush_detected:
        inrush_supporting.append("COMTRADE summary indicates inrush")

    if load_percent is not None and load_percent <= 10:
        inrush_supporting.append("Low load condition may support energization/inrush scenario")

    for item in ["COMTRADE waveform", "Recent maintenance history"]:
        if item in missing:
            inrush_missing.append(item)

    inrush_confidence = "low"
    if inrush_detected:
        inrush_confidence = "medium"
    if inrush_detected and load_percent is not None and load_percent <= 10:
        inrush_confidence = "high"

    evaluations.append({
        "hypothesis": "Inrush or abnormal energization condition",
        "confidence": inrush_confidence,
        "supporting_evidence": inrush_supporting,
        "missing_evidence": inrush_missing,
        "risk": "medium",
        "recommended_next_action": "Review energization timing, harmonic restraint behavior, and recent switching or maintenance history.",
    })

    return evaluations
