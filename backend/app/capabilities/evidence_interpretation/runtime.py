from __future__ import annotations

from app.capabilities.evidence_interpretation.contracts import (
    EvidenceInterpretationItem,
    EvidenceInterpretationRequest,
    EvidenceInterpretationResult,
)


def execute_evidence_interpretation(
    *,
    request: EvidenceInterpretationRequest,
) -> EvidenceInterpretationResult:
    """
    Interpret recognized evidence conservatively.

    This runtime performs evidence interpretation only.
    It does not determine root cause, confidence,
    readiness, safety state, or engineering decisions.
    """

    if not isinstance(
        request,
        EvidenceInterpretationRequest,
    ):
        raise TypeError(
            "execute_evidence_interpretation requires an "
            "EvidenceInterpretationRequest."
        )

    interpretations: list[
        EvidenceInterpretationItem
    ] = []

    unresolved_evidence: list[str] = []

    for evidence in request.available_evidence:
        interpretation = _interpret_evidence(
            evidence
        )

        if interpretation is None:
            unresolved_evidence.append(evidence)
            continue

        interpretations.append(interpretation)

    return EvidenceInterpretationResult(
        interpretations=tuple(interpretations),
        unresolved_evidence=tuple(
            unresolved_evidence
        ),
    )


def _interpret_evidence(
    evidence: str,
) -> EvidenceInterpretationItem | None:
    normalized = evidence.strip().casefold()

    if normalized == "buchholz relay status":
        return EvidenceInterpretationItem(
            evidence=evidence,
            interpretation=(
                "Buchholz relay status is available for "
                "assessment of gas accumulation or oil "
                "movement associated with an internal "
                "transformer disturbance."
            ),
            engineering_significance=(
                "This evidence can support assessment of "
                "possible internal transformer conditions "
                "when correlated with DGA, relay records, "
                "and other available evidence."
            ),
        )

    if normalized == "dga report":
        return EvidenceInterpretationItem(
            evidence=evidence,
            interpretation=(
                "Dissolved gas analysis information is "
                "available for assessment of transformer "
                "oil and insulation condition."
            ),
            engineering_significance=(
                "DGA can provide evidence associated with "
                "thermal or electrical degradation, but "
                "must be interpreted using gas patterns, "
                "trends, and operating context."
            ),
        )

    if normalized == "comtrade waveform":
        return EvidenceInterpretationItem(
            evidence=evidence,
            interpretation=(
                "Disturbance waveform data is available "
                "for examination of electrical quantities "
                "during the event."
            ),
            engineering_significance=(
                "Waveform analysis can help distinguish "
                "event characteristics and should be "
                "correlated with relay targets, breaker "
                "states, and transformer condition data."
            ),
        )

    if normalized == "oil temperature":
        return EvidenceInterpretationItem(
            evidence=evidence,
            interpretation=(
                "Transformer oil temperature information "
                "is available for assessment of thermal "
                "condition around the event."
            ),
            engineering_significance=(
                "Temperature provides operating-condition "
                "context but does not independently "
                "establish the cause of a differential "
                "protection operation."
            ),
        )

    if normalized == "load before trip":
        return EvidenceInterpretationItem(
            evidence=evidence,
            interpretation=(
                "Transformer loading information before "
                "the trip is available."
            ),
            engineering_significance=(
                "Pre-event loading provides operating "
                "context for thermal and electrical "
                "assessment but does not independently "
                "identify the initiating condition."
            ),
        )

    return None
