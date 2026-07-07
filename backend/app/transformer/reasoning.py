from __future__ import annotations


def evaluate_differential_trip_hypotheses(
    available_evidence: list[str],
    missing_required_evidence: list[str],
    buchholz_alarm: bool | None,
    comtrade_available: bool,
    dga_available: bool,
    oil_temperature_c: float | None,
    load_percent: float | None,
) -> list[dict]:
    available = set(available_evidence)
    missing = set(missing_required_evidence)

    evaluations: list[dict] = []

    internal_supporting = []
    internal_missing = []

    if "Differential relay targets" in available:
        internal_supporting.append("Differential relay targets available")

    if "DGA report" in available or dga_available:
        internal_supporting.append("DGA report available")

    if buchholz_alarm is True:
        internal_supporting.append("Buchholz alarm is active")

    if oil_temperature_c is not None and oil_temperature_c >= 90:
        internal_supporting.append("High oil temperature observed")

    for item in ["COMTRADE waveform", "DGA report", "Buchholz relay status", "Visual inspection"]:
        if item in missing:
            internal_missing.append(item)

    internal_confidence = "low"
    if buchholz_alarm is True and ("DGA report" in available or dga_available):
        internal_confidence = "high"
    elif internal_supporting:
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

    for item in ["COMTRADE waveform", "HV/LV breaker status", "Differential relay targets"]:
        if item in missing:
            external_missing.append(item)

    external_confidence = "low"
    if ("COMTRADE waveform" in available or comtrade_available) and "HV/LV breaker status" in available:
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

    for item in ["Relay event report", "COMTRADE waveform", "Differential relay targets"]:
        if item in missing:
            protection_missing.append(item)

    protection_confidence = "low"
    if "Relay event report" in available and ("COMTRADE waveform" in available or comtrade_available):
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

    for item in ["COMTRADE waveform", "Differential relay targets"]:
        if item in missing:
            ct_missing.append(item)

    ct_confidence = "low"
    if "Differential relay targets" in available and ("COMTRADE waveform" in available or comtrade_available):
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

    if load_percent is not None and load_percent <= 10:
        inrush_supporting.append("Low load condition may support energization/inrush scenario")

    for item in ["COMTRADE waveform", "Recent maintenance history"]:
        if item in missing:
            inrush_missing.append(item)

    inrush_confidence = "low"
    if ("COMTRADE waveform" in available or comtrade_available) and load_percent is not None and load_percent <= 10:
        inrush_confidence = "medium"

    evaluations.append({
        "hypothesis": "Inrush or abnormal energization condition",
        "confidence": inrush_confidence,
        "supporting_evidence": inrush_supporting,
        "missing_evidence": inrush_missing,
        "risk": "medium",
        "recommended_next_action": "Review energization timing, harmonic restraint behavior, and recent switching or maintenance history.",
    })

    return evaluations
