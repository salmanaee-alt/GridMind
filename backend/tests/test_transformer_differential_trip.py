from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_transformer_differential_trip_with_missing_evidence():
    payload = {
        "asset_id": "T1",
        "voltage_level": "230/13.8 kV",
        "event_description": "Transformer tripped by differential relay",
        "relay_name": "87T",
        "available_data": ["Relay event report"],
        "missing_data": [],
        "comtrade_available": False,
        "dga_available": False,
        "buchholz_alarm": None,
        "oil_temperature_c": 72,
        "load_percent": 65,
        "notes": "No smoke reported. Initial site inspection pending."
    }

    response = client.post("/transformer/differential-trip", json=payload)

    assert response.status_code == 200

    data = response.json()
    session = data["session"]
    decision = session["decisions"][0]

    assert data["role"] == "Transformer Engineer"
    assert data["event_type"] == "differential_trip"
    assert data["status"] == "completed"

    assert decision["decision_type"] == "evidence_required_before_final_decision"
    assert decision["confidence"] == "low"
    assert decision["safety_position"] == "conservative"

    reason_step = next(
        step for step in session["reasoning_steps"]
        if step["stage"] == "reason"
    )

    assert reason_step["data"]["final_conclusion_allowed"] is False


def test_transformer_differential_trip_with_complete_evidence():
    payload = {
        "asset_id": "T1",
        "voltage_level": "230/13.8 kV",
        "event_description": "Transformer tripped by differential relay",
        "relay_name": "87T",
        "available_data": [
            "Relay event report",
            "COMTRADE waveform",
            "Differential relay targets",
            "HV/LV breaker status",
            "DGA report",
            "Buchholz relay status",
            "Oil temperature",
            "Load before trip",
            "Visual inspection",
            "Recent maintenance history"
        ],
        "missing_data": [],
        "comtrade_available": True,
        "dga_available": True,
        "buchholz_alarm": False,
        "oil_temperature_c": 72,
        "load_percent": 65,
        "notes": "All required evidence is available for preliminary engineering review."
    }

    response = client.post("/transformer/differential-trip", json=payload)

    assert response.status_code == 200

    data = response.json()
    session = data["session"]
    decision = session["decisions"][0]

    assert data["role"] == "Transformer Engineer"
    assert data["event_type"] == "differential_trip"
    assert data["status"] == "completed"

    assert decision["decision_type"] == "engineering_recommendation"
    assert decision["confidence"] == "medium"
    assert decision["safety_position"] == "controlled"

    reason_step = next(
        step for step in session["reasoning_steps"]
        if step["stage"] == "reason"
    )

    assert reason_step["data"]["final_conclusion_allowed"] is True


def test_transformer_differential_trip_hypotheses_are_evaluated():
    payload = {
        "asset_id": "T1",
        "voltage_level": "230/13.8 kV",
        "event_description": "Transformer tripped by differential relay",
        "relay_name": "87T",
        "available_data": ["Relay event report"],
        "missing_data": [],
        "comtrade_available": False,
        "dga_available": False,
        "buchholz_alarm": None,
        "oil_temperature_c": 72,
        "load_percent": 65,
        "notes": "No smoke reported. Initial site inspection pending."
    }

    response = client.post("/transformer/differential-trip", json=payload)

    assert response.status_code == 200

    data = response.json()
    hypotheses = data["session"]["hypotheses"]

    assert len(hypotheses) == 5

    for hypothesis in hypotheses:
        assert "hypothesis" in hypothesis
        assert "confidence" in hypothesis
        assert "supporting_evidence" in hypothesis
        assert "missing_evidence" in hypothesis
        assert "risk" in hypothesis
        assert "recommended_next_action" in hypothesis
        assert hypothesis["source"] == "Transformer Reasoning v0.3"

        assert hypothesis["confidence"] in ["low", "medium", "high"]
        assert isinstance(hypothesis["supporting_evidence"], list)
        assert isinstance(hypothesis["missing_evidence"], list)


def test_transformer_response_uses_top_ranked_hypothesis_not_most_likely():
    payload = {
        "asset_id": "T1",
        "voltage_level": "230/13.8 kV",
        "event_description": "Transformer tripped by differential relay",
        "relay_name": "87T",
        "available_data": ["Relay event report"],
        "missing_data": [],
        "comtrade_available": False,
        "dga_available": False,
        "buchholz_alarm": None,
        "oil_temperature_c": 72,
        "load_percent": 65,
        "notes": "No smoke reported. Initial site inspection pending."
    }

    response = client.post("/transformer/differential-trip", json=payload)

    assert response.status_code == 200

    data = response.json()
    session = data["session"]

    response_as_text = str(data)

    assert "top_ranked_hypothesis" in response_as_text
    assert "most_likely_hypothesis" not in response_as_text

    decision = session["decisions"][0]
    report = session["reports"][0]

    assert "top_ranked_hypothesis" in decision
    assert "top_ranked_hypothesis" in report
    assert "ranked_hypotheses" in report
