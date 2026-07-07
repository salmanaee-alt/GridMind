from __future__ import annotations


TRANSFORMER_EVENT_KNOWLEDGE = {
    "differential_trip": {
        "description": "Transformer differential relay trip investigation",
        "risk_level": "high",
        "initial_safety_position": "Do not re-energize until protection records and transformer condition are reviewed.",
        "required_evidence": [
            "Relay event report",
            "COMTRADE waveform",
            "Differential relay targets",
            "HV/LV breaker status",
            "DGA report",
            "Buchholz relay status",
            "Oil temperature",
            "Load before trip",
            "Visual inspection",
            "Recent maintenance history",
        ],
        "initial_hypotheses": [
            "Internal transformer fault",
            "External fault with CT saturation",
            "Protection misoperation",
            "CT circuit issue",
            "Inrush or abnormal energization condition",
        ],
    }
}


def get_transformer_event_knowledge(event_type: str) -> dict:
    knowledge = TRANSFORMER_EVENT_KNOWLEDGE.get(event_type)

    if knowledge is None:
        raise ValueError(f"Unknown transformer event type: {event_type}")

    return knowledge
