from __future__ import annotations

from app.brain.engineering_brain import EngineeringBrain
from app.brain.engineering_session import EngineeringSession
from app.transformer.knowledge import get_transformer_event_knowledge
from app.transformer.reasoning import evaluate_differential_trip_hypotheses
from app.transformer.schemas import TransformerDifferentialTripRequest


def clean_text(value: str | None) -> str | None:
    if value is None:
        return None

    cleaned = value.strip()

    if not cleaned:
        return None

    return cleaned


def clean_list(values: list[str]) -> list[str]:
    cleaned_values: list[str] = []

    for value in values:
        cleaned = clean_text(value)
        if cleaned is not None:
            cleaned_values.append(cleaned)

    return cleaned_values


class TransformerEngineer:
    def investigate_differential_trip(self, request: TransformerDifferentialTripRequest) -> dict:
        knowledge = get_transformer_event_knowledge("differential_trip")

        asset_id = clean_text(request.asset_id) or "Unknown Transformer"
        voltage_level = clean_text(request.voltage_level)
        event_description = clean_text(request.event_description) or "Transformer differential relay trip"
        relay_name = clean_text(request.relay_name)
        notes = clean_text(request.notes)

        known_available = set(clean_list(request.available_data))

        if request.comtrade_available:
            known_available.add("COMTRADE waveform")

        if request.dga_available:
            known_available.add("DGA report")

        if request.buchholz_alarm is not None:
            known_available.add("Buchholz relay status")

        if request.oil_temperature_c is not None:
            known_available.add("Oil temperature")

        if request.load_percent is not None:
            known_available.add("Load before trip")

        missing_required_evidence = [
            item
            for item in knowledge["required_evidence"]
            if item not in known_available
        ]

        for item in clean_list(request.missing_data):
            if item not in missing_required_evidence:
                missing_required_evidence.append(item)

        available_evidence = sorted(list(known_available))

        evidence_metadata = [
            metadata.model_dump()
            for metadata in request.evidence_metadata
        ]

        hypothesis_evaluations = evaluate_differential_trip_hypotheses(
            available_evidence=available_evidence,
            missing_required_evidence=missing_required_evidence,
            buchholz_alarm=request.buchholz_alarm,
            comtrade_available=request.comtrade_available,
            dga_available=request.dga_available,
            oil_temperature_c=request.oil_temperature_c,
            load_percent=request.load_percent,
            relay_targets=request.relay_targets,
            dga_status=request.dga_status,
            comtrade_summary=request.comtrade_summary,
        hv_breaker_status=request.hv_breaker_status,
        lv_breaker_status=request.lv_breaker_status,        )

        session = EngineeringSession(
            title=knowledge["description"],
            metadata={
                "engineering_role": "Transformer Engineer",
                "event_type": "differential_trip",
                "risk_level": knowledge["risk_level"],
                "asset_id": asset_id,
                "voltage_level": voltage_level,
            },
        )

        session.add_observation({
            "asset_id": asset_id,
            "voltage_level": voltage_level,
            "event": event_description,
            "relay_name": relay_name,
            "oil_temperature_c": request.oil_temperature_c,
            "load_percent": request.load_percent,
            "buchholz_alarm": request.buchholz_alarm,
            "comtrade_available": request.comtrade_available,
            "dga_available": request.dga_available,
            "relay_targets": request.relay_targets,
            "dga_status": request.dga_status,
            "comtrade_summary": request.comtrade_summary,
            "evidence_metadata": evidence_metadata,
            "notes": notes,
            "initial_safety_position": knowledge["initial_safety_position"],
            "available_evidence": available_evidence,
            "missing_required_evidence": missing_required_evidence,
            "source": "Transformer Knowledge v0.1",
        })

        for evaluation in hypothesis_evaluations:
            session.add_hypothesis({
                "hypothesis": evaluation["hypothesis"],
                "confidence": evaluation["confidence"],
                "supporting_evidence": evaluation["supporting_evidence"],
                "missing_evidence": evaluation["missing_evidence"],
                "conflicts": evaluation.get("conflicts", []),
                "risk": evaluation["risk"],
                "recommended_next_action": evaluation["recommended_next_action"],
                "source": "Transformer Reasoning v0.10",
            })

        brain = EngineeringBrain()
        completed_session = brain.run(session)

        return {
            "role": "Transformer Engineer",
            "event_type": "differential_trip",
            "status": completed_session.status.value,
            "session": completed_session.to_dict(),
        }


