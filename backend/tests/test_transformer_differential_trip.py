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
    assert decision["confidence"] in ["low", "medium"]
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
        assert "conflicts" in hypothesis
        assert "recommended_next_action" in hypothesis
        assert hypothesis["source"] == "Transformer Reasoning v0.5"

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


def test_transformer_content_reasoning_ranks_internal_fault_high():
    payload = {
        "asset_id": "T1",
        "voltage_level": "230/13.8 kV",
        "event_description": "Transformer tripped by differential relay",
        "relay_name": "87T",
        "available_data": [
            "Relay event report",
            "COMTRADE waveform",
            "Differential relay targets",
            "DGA report",
            "Buchholz relay status",
            "Oil temperature",
            "Load before trip"
        ],
        "missing_data": [],
        "comtrade_available": True,
        "dga_available": True,
        "buchholz_alarm": False,
        "oil_temperature_c": 72,
        "load_percent": 65,
        "relay_targets": ["87T differential operated"],
        "dga_status": "abnormal",
        "comtrade_summary": "no_inrush",
        "notes": "Relay target shows differential operation. DGA abnormal. No inrush signature observed."
    }

    response = client.post("/transformer/differential-trip", json=payload)

    assert response.status_code == 200

    data = response.json()
    session = data["session"]

    top_ranked = session["decisions"][0]["top_ranked_hypothesis"]

    assert top_ranked["hypothesis"] == "Internal transformer fault"
    assert top_ranked["confidence"] == "high"
    assert top_ranked["source"] == "Transformer Reasoning v0.5"

    assert "DGA status is abnormal." in top_ranked["supporting_evidence"]
    assert "COMTRADE summary does not indicate inrush." in top_ranked["supporting_evidence"]

    assert session["decisions"][0]["decision_type"] == "evidence_required_before_final_decision"


def test_transformer_content_reasoning_detects_evidence_conflict():
    payload = {
        "asset_id": "T1",
        "voltage_level": "230/13.8 kV",
        "event_description": "Transformer tripped by differential relay",
        "relay_name": "87T",
        "available_data": [
            "Relay event report",
            "COMTRADE waveform",
            "Differential relay targets",
            "DGA report",
            "Buchholz relay status",
            "Oil temperature",
            "Load before trip"
        ],
        "missing_data": [],
        "comtrade_available": True,
        "dga_available": True,
        "buchholz_alarm": False,
        "oil_temperature_c": 72,
        "load_percent": 65,
        "relay_targets": ["87T differential operated"],
        "dga_status": "normal",
        "comtrade_summary": "no_inrush",
        "notes": "Relay target shows differential operation, but DGA is normal."
    }

    response = client.post("/transformer/differential-trip", json=payload)

    assert response.status_code == 200

    data = response.json()
    hypotheses = data["session"]["hypotheses"]

    internal_fault = next(
        hypothesis for hypothesis in hypotheses
        if hypothesis["hypothesis"] == "Internal transformer fault"
    )

    assert internal_fault["confidence"] in ["low", "medium"]
    assert len(internal_fault["conflicts"]) >= 1
    assert internal_fault["conflicts"][0]["severity"] == "medium"


def test_transformer_evidence_quality_scoring_is_reported():
    payload = {
        "asset_id": "T1",
        "voltage_level": "230/13.8 kV",
        "event_description": "Transformer tripped by differential relay",
        "relay_name": "87T",
        "available_data": [
            "Relay event report",
            "COMTRADE waveform",
            "Differential relay targets",
            "DGA report",
            "Buchholz relay status",
            "Oil temperature",
            "Load before trip"
        ],
        "missing_data": [],
        "comtrade_available": True,
        "dga_available": True,
        "buchholz_alarm": False,
        "oil_temperature_c": 72,
        "load_percent": 65,
        "relay_targets": ["87T differential operated"],
        "dga_status": "normal",
        "comtrade_summary": "no_inrush",
        "notes": "Relay target shows differential operation, but DGA is normal."
    }

    response = client.post("/transformer/differential-trip", json=payload)

    assert response.status_code == 200

    data = response.json()
    decision = data["session"]["decisions"][0]
    report = data["session"]["reports"][0]
    reason_step = next(
        step for step in data["session"]["reasoning_steps"]
        if step["stage"] == "reason"
    )

    assert "evidence_quality" in decision
    assert "evidence_quality" in report
    assert "evidence_quality" in reason_step["data"]

    evidence_quality = decision["evidence_quality"]

    assert "quality_score" in evidence_quality
    assert "quality_level" in evidence_quality
    assert "completeness_score" in evidence_quality
    assert "directness_score" in evidence_quality
    assert "conflict_penalty" in evidence_quality
    assert "quality_notes" in evidence_quality

    assert evidence_quality["quality_level"] in ["low", "medium", "high"]
    assert evidence_quality["unresolved_conflict_count"] >= 1
    assert evidence_quality["conflict_penalty"] > 0


def test_transformer_conflict_blocks_final_decision_even_with_complete_evidence():
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
        "relay_targets": ["87T differential operated"],
        "dga_status": "normal",
        "comtrade_summary": "no_inrush",
        "notes": "All required evidence is available, but DGA is normal while relay target indicates differential operation and COMTRADE indicates no inrush."
    }

    response = client.post("/transformer/differential-trip", json=payload)

    assert response.status_code == 200

    data = response.json()
    decision = data["session"]["decisions"][0]
    reason_step = next(
        step for step in data["session"]["reasoning_steps"]
        if step["stage"] == "reason"
    )

    assert decision["decision_type"] == "evidence_required_before_final_decision"
    assert decision["confidence"] == "low"
    assert decision["safety_position"] == "conservative"
    assert decision["conflict_blocking"] is True
    assert len(decision["unresolved_conflicts"]) >= 1

    assert reason_step["data"]["final_conclusion_allowed"] is False
    assert reason_step["data"]["conflict_blocking"] is True
    assert len(reason_step["data"]["unresolved_conflicts"]) >= 1

    assert decision["required_next_evidence"] == []
