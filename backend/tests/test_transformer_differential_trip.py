from fastapi.testclient import TestClient

from app.main import app
from app.transformer.reasoning import evaluate_differential_trip_hypotheses
from app.brain.engineering_brain import EngineeringBrain


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
        assert hypothesis["source"] == "Transformer Reasoning v0.10"

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
    assert top_ranked["source"] == "Transformer Reasoning v0.10"

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


def test_transformer_evidence_metadata_is_reported_in_observation():
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
        "evidence_metadata": [
            {
                "evidence_name": "Relay event report",
                "source_type": "relay",
                "timestamp_relation": "during_event",
                "verified": True
            },
            {
                "evidence_name": "COMTRADE waveform",
                "source_type": "comtrade",
                "timestamp_relation": "during_event",
                "verified": True
            },
            {
                "evidence_name": "DGA report",
                "source_type": "lab",
                "timestamp_relation": "after_event",
                "verified": True
            }
        ],
        "notes": "Evidence metadata is provided for v0.6 validation."
    }

    response = client.post("/transformer/differential-trip", json=payload)

    assert response.status_code == 200

    data = response.json()
    observation = data["session"]["observations"][0]

    assert "evidence_metadata" in observation
    assert len(observation["evidence_metadata"]) == 3

    relay_metadata = observation["evidence_metadata"][0]

    assert relay_metadata["evidence_name"] == "Relay event report"
    assert relay_metadata["source_type"] == "relay"
    assert relay_metadata["timestamp_relation"] == "during_event"
    assert relay_metadata["verified"] is True


def test_transformer_metadata_aware_evidence_quality_is_reported():
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
        "evidence_metadata": [
            {
                "evidence_name": "Relay event report",
                "source_type": "relay",
                "timestamp_relation": "during_event",
                "verified": True
            },
            {
                "evidence_name": "COMTRADE waveform",
                "source_type": "comtrade",
                "timestamp_relation": "during_event",
                "verified": True
            },
            {
                "evidence_name": "DGA report",
                "source_type": "lab",
                "timestamp_relation": "after_event",
                "verified": True
            }
        ],
        "notes": "Metadata-aware evidence quality validation."
    }

    response = client.post("/transformer/differential-trip", json=payload)

    assert response.status_code == 200

    data = response.json()
    decision = data["session"]["decisions"][0]
    reason_step = next(
        step for step in data["session"]["reasoning_steps"]
        if step["stage"] == "reason"
    )

    evidence_quality = decision["evidence_quality"]

    assert "metadata_score" in evidence_quality
    assert "verified_evidence_ratio" in evidence_quality
    assert "source_reliability_score" in evidence_quality
    assert "metadata_quality_notes" in evidence_quality

    assert evidence_quality["metadata_score"] > 0
    assert evidence_quality["verified_evidence_ratio"] > 0
    assert evidence_quality["source_reliability_score"] > 0
    assert len(evidence_quality["metadata_quality_notes"]) >= 1

    assert reason_step["data"]["evidence_quality"]["metadata_score"] == evidence_quality["metadata_score"]


def test_transformer_rejects_evidence_metadata_name_not_in_evidence_lists():
    payload = {
        "asset_id": "T1",
        "voltage_level": "230/13.8 kV",
        "event_description": "Transformer tripped by differential relay",
        "relay_name": "87T",
        "available_data": [
            "Relay event report",
            "COMTRADE waveform",
            "Differential relay targets",
            "DGA report"
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
        "evidence_metadata": [
            {
                "evidence_name": "DGA Lab File",
                "source_type": "lab",
                "timestamp_relation": "after_event",
                "verified": True
            }
        ],
        "notes": "This request should fail because evidence metadata name does not match available_data or missing_data."
    }

    response = client.post("/transformer/differential-trip", json=payload)

    assert response.status_code == 422


def test_transformer_accepts_evidence_metadata_for_flag_added_evidence():
    payload = {
        "asset_id": "T1",
        "voltage_level": "230/13.8 kV",
        "event_description": "Transformer tripped by differential relay",
        "relay_name": "87T",
        "available_data": [
            "Relay event report",
            "Differential relay targets"
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
        "evidence_metadata": [
            {
                "evidence_name": "COMTRADE waveform",
                "source_type": "comtrade",
                "timestamp_relation": "during_event",
                "verified": True
            },
            {
                "evidence_name": "DGA report",
                "source_type": "lab",
                "timestamp_relation": "after_event",
                "verified": True
            },
            {
                "evidence_name": "Buchholz relay status",
                "source_type": "relay",
                "timestamp_relation": "during_event",
                "verified": True
            },
            {
                "evidence_name": "Oil temperature",
                "source_type": "scada",
                "timestamp_relation": "during_event",
                "verified": True
            },
            {
                "evidence_name": "Load before trip",
                "source_type": "scada",
                "timestamp_relation": "before_event",
                "verified": True
            }
        ],
        "notes": "Metadata references evidence added by boolean and value flags."
    }

    response = client.post("/transformer/differential-trip", json=payload)

    assert response.status_code == 200

    data = response.json()
    observation = data["session"]["observations"][0]
    metadata_names = [
        item["evidence_name"]
        for item in observation["evidence_metadata"]
    ]

    assert "COMTRADE waveform" in metadata_names
    assert "DGA report" in metadata_names
    assert "Buchholz relay status" in metadata_names
    assert "Oil temperature" in metadata_names
    assert "Load before trip" in metadata_names


def test_transformer_timestamp_relation_aware_evidence_quality_is_reported():
    payload = {
        "asset_id": "T1",
        "voltage_level": "230/13.8 kV",
        "event_description": "Transformer tripped by differential relay",
        "relay_name": "87T",
        "available_data": [
            "Relay event report",
            "Differential relay targets"
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
        "evidence_metadata": [
            {
                "evidence_name": "Relay event report",
                "source_type": "relay",
                "timestamp_relation": "during_event",
                "verified": True
            },
            {
                "evidence_name": "COMTRADE waveform",
                "source_type": "comtrade",
                "timestamp_relation": "during_event",
                "verified": True
            },
            {
                "evidence_name": "DGA report",
                "source_type": "lab",
                "timestamp_relation": "after_event",
                "verified": True
            },
            {
                "evidence_name": "Load before trip",
                "source_type": "scada",
                "timestamp_relation": "before_event",
                "verified": True
            }
        ],
        "notes": "Timestamp-aware evidence quality validation."
    }

    response = client.post("/transformer/differential-trip", json=payload)

    assert response.status_code == 200

    data = response.json()
    decision = data["session"]["decisions"][0]
    evidence_quality = decision["evidence_quality"]

    assert "timestamp_relation_score" in evidence_quality
    assert evidence_quality["timestamp_relation_score"] > 0
    assert "Evidence timing" in " ".join(evidence_quality["metadata_quality_notes"])


def test_transformer_freshness_aware_evidence_quality_is_reported():
    payload = {
        "asset_id": "T1",
        "voltage_level": "230/13.8 kV",
        "event_description": "Transformer tripped by differential relay",
        "relay_name": "87T",
        "available_data": [
            "Relay event report",
            "Differential relay targets"
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
        "evidence_metadata": [
            {
                "evidence_name": "Relay event report",
                "source_type": "relay",
                "timestamp_relation": "during_event",
                "evidence_age_days": 0,
                "verified": True
            },
            {
                "evidence_name": "COMTRADE waveform",
                "source_type": "comtrade",
                "timestamp_relation": "during_event",
                "evidence_age_days": 0,
                "verified": True
            },
            {
                "evidence_name": "DGA report",
                "source_type": "lab",
                "timestamp_relation": "after_event",
                "evidence_age_days": 2,
                "verified": True
            },
            {
                "evidence_name": "Load before trip",
                "source_type": "scada",
                "timestamp_relation": "before_event",
                "evidence_age_days": 1,
                "verified": True
            }
        ],
        "notes": "Freshness-aware evidence quality validation."
    }

    response = client.post("/transformer/differential-trip", json=payload)

    assert response.status_code == 200

    data = response.json()
    decision = data["session"]["decisions"][0]
    evidence_quality = decision["evidence_quality"]

    assert "freshness_score" in evidence_quality
    assert evidence_quality["freshness_score"] > 0
    assert "Evidence is recent." in evidence_quality["metadata_quality_notes"]

def test_transformer_breaker_failed_to_open_creates_conflict():
    evaluations = evaluate_differential_trip_hypotheses(
        available_evidence=[
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
        missing_required_evidence=[],
        buchholz_alarm=False,
        comtrade_available=True,
        dga_available=True,
        oil_temperature_c=72,
        load_percent=65,
        relay_targets=["87T differential operated"],
        dga_status="abnormal",
        comtrade_summary="no_inrush",
        hv_breaker_status="failed_to_open",
        lv_breaker_status="open",
    )

    response_text = str(evaluations).lower()

    assert "failed to open" in response_text
    assert "breaker" in response_text
    assert "high" in response_text


def test_transformer_breaker_both_open_supports_isolation_without_conflict():
    evaluations = evaluate_differential_trip_hypotheses(
        available_evidence=[
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
        missing_required_evidence=[],
        buchholz_alarm=False,
        comtrade_available=True,
        dga_available=True,
        oil_temperature_c=72,
        load_percent=65,
        relay_targets=["87T differential operated"],
        dga_status="abnormal",
        comtrade_summary="no_inrush",
        hv_breaker_status="open",
        lv_breaker_status="open",
    )

    response_text = str(evaluations).lower()

    assert "successful transformer isolation" in response_text
    assert "failed to open" not in response_text
    assert "remained closed" not in response_text


def test_transformer_breaker_one_closed_creates_medium_conflict():
    evaluations = evaluate_differential_trip_hypotheses(
        available_evidence=[
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
        missing_required_evidence=[],
        buchholz_alarm=False,
        comtrade_available=True,
        dga_available=True,
        oil_temperature_c=72,
        load_percent=65,
        relay_targets=["87T differential operated"],
        dga_status="abnormal",
        comtrade_summary="no_inrush",
        hv_breaker_status="closed",
        lv_breaker_status="open",
    )

    response_text = str(evaluations).lower()

    assert "remained closed" in response_text
    assert "breaker" in response_text
    assert "medium" in response_text


def test_transformer_breaker_tripped_supports_isolation_without_conflict():
    evaluations = evaluate_differential_trip_hypotheses(
        available_evidence=[
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
        missing_required_evidence=[],
        buchholz_alarm=False,
        comtrade_available=True,
        dga_available=True,
        oil_temperature_c=72,
        load_percent=65,
        relay_targets=["87T differential operated"],
        dga_status="abnormal",
        comtrade_summary="no_inrush",
        hv_breaker_status="tripped",
        lv_breaker_status="tripped",
    )

    response_text = str(evaluations).lower()

    assert "successful transformer isolation" in response_text
    assert "failed to open" not in response_text
    assert "remained closed" not in response_text

def test_transformer_breaker_failure_becomes_global_safety_conflict():
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
        "dga_status": "abnormal",
        "comtrade_summary": "no_inrush",
        "hv_breaker_status": "failed_to_open",
        "lv_breaker_status": "open",
        "notes": "Breaker post-trip position review required."
    }

    response = client.post("/transformer/differential-trip", json=payload)

    assert response.status_code == 200

    data = response.json()
    session = data["session"]
    decision = session["decisions"][0]

    reason_step = next(
        step for step in session["reasoning_steps"]
        if step["stage"] == "reason"
    )

    assert decision["decision_type"] == "evidence_required_before_final_decision"
    assert decision["confidence"] == "low"
    assert decision["safety_position"] == "conservative"
    assert decision["conflict_blocking"] is True

    assert reason_step["data"]["final_conclusion_allowed"] is False
    assert reason_step["data"]["conflict_blocking"] is True

    unresolved_conflicts = reason_step["data"]["unresolved_conflicts"]
    conflict_text = str(unresolved_conflicts).lower()

    assert len(unresolved_conflicts) >= 1
    assert "failed to open" in conflict_text
    assert "breaker" in conflict_text
    assert "high" in conflict_text


def test_low_severity_conflict_is_not_blocking():
    brain = object.__new__(EngineeringBrain)

    conflicts = [
        {
            "conflict": "Minor non-safety inconsistency in supporting evidence.",
            "severity": "low",
            "recommended_verification": "Review during normal engineering validation.",
        }
    ]

    blocking_conflicts = brain._extract_blocking_conflicts(conflicts)

    assert blocking_conflicts == []


def test_medium_high_and_critical_conflicts_are_blocking():
    brain = object.__new__(EngineeringBrain)

    conflicts = [
        {
            "conflict": "Medium severity evidence conflict.",
            "severity": "medium",
            "recommended_verification": "Resolve before final conclusion.",
        },
        {
            "conflict": "High severity safety conflict.",
            "severity": "high",
            "recommended_verification": "Resolve before re-energization.",
        },
        {
            "conflict": "Critical safety conflict.",
            "severity": "critical",
            "recommended_verification": "Apply safety lock until resolved.",
        },
    ]

    blocking_conflicts = brain._extract_blocking_conflicts(conflicts)

    assert len(blocking_conflicts) == 3
    assert all(
        conflict["severity"] in ["medium", "high", "critical"]
        for conflict in blocking_conflicts
    )

def test_blocking_conflicts_are_visible_in_api_response():
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
        "dga_status": "abnormal",
        "comtrade_summary": "no_inrush",
        "hv_breaker_status": "failed_to_open",
        "lv_breaker_status": "open",
        "notes": "Breaker post-trip position review required."
    }

    response = client.post("/transformer/differential-trip", json=payload)

    assert response.status_code == 200

    data = response.json()
    session = data["session"]

    reason_step = next(
        step for step in session["reasoning_steps"]
        if step["stage"] == "reason"
    )

    decision = session["decisions"][0]
    report = session["reports"][0]

    assert "unresolved_conflicts" in reason_step["data"]
    assert "blocking_conflicts" in reason_step["data"]
    assert reason_step["data"]["conflict_blocking"] is True

    assert "unresolved_conflicts" in decision
    assert "blocking_conflicts" in decision
    assert decision["conflict_blocking"] is True

    assert "unresolved_conflicts" in report
    assert "blocking_conflicts" in report
    assert report["conflict_blocking"] is True

    blocking_text = str(reason_step["data"]["blocking_conflicts"]).lower()

    assert "failed to open" in blocking_text
    assert "breaker" in blocking_text
    assert "high" in blocking_text

def test_re_energization_readiness_is_not_ready_with_missing_evidence():
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
        "notes": "Initial site inspection pending."
    }

    response = client.post("/transformer/differential-trip", json=payload)

    assert response.status_code == 200

    data = response.json()
    decision = data["session"]["decisions"][0]
    report = data["session"]["reports"][0]

    assert decision["re_energization_readiness"] == "not_ready"
    assert report["re_energization_readiness"] == "not_ready"


def test_re_energization_readiness_is_not_ready_with_blocking_conflict():
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
        "dga_status": "abnormal",
        "comtrade_summary": "no_inrush",
        "hv_breaker_status": "failed_to_open",
        "lv_breaker_status": "open",
        "notes": "Breaker post-trip position review required."
    }

    response = client.post("/transformer/differential-trip", json=payload)

    assert response.status_code == 200

    data = response.json()
    decision = data["session"]["decisions"][0]
    report = data["session"]["reports"][0]

    assert decision["conflict_blocking"] is True
    assert decision["re_energization_readiness"] == "not_ready"
    assert report["re_energization_readiness"] == "not_ready"


def test_re_energization_readiness_is_conditionally_ready_with_complete_clean_evidence():
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
        "relay_targets": [],
        "dga_status": "normal",
        "comtrade_summary": "inrush_detected",
        "hv_breaker_status": "open",
        "lv_breaker_status": "open",
        "notes": "All required evidence is available with no blocking conflict."
    }

    response = client.post("/transformer/differential-trip", json=payload)

    assert response.status_code == 200

    data = response.json()
    decision = data["session"]["decisions"][0]
    report = data["session"]["reports"][0]

    assert decision["conflict_blocking"] is False
    assert decision["re_energization_readiness"] == "conditionally_ready_for_engineering_review"
    assert report["re_energization_readiness"] == "conditionally_ready_for_engineering_review"

def test_asset_condition_abnormal_dga_forces_not_ready():
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
        "relay_targets": [],
        "dga_status": "abnormal",
        "comtrade_summary": "inrush_detected",
        "hv_breaker_status": "open",
        "lv_breaker_status": "open",
        "notes": "DGA abnormal with otherwise complete evidence."
    }

    response = client.post("/transformer/differential-trip", json=payload)

    assert response.status_code == 200

    data = response.json()
    decision = data["session"]["decisions"][0]
    report = data["session"]["reports"][0]

    assert decision["re_energization_readiness"] == "not_ready"
    assert report["re_energization_readiness"] == "not_ready"

    flags_text = str(decision["asset_condition_readiness"]["asset_condition_flags"]).lower()
    assert "dga" in flags_text
    assert "abnormal" in flags_text


def test_asset_condition_buchholz_alarm_forces_not_ready():
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
        "buchholz_alarm": True,
        "oil_temperature_c": 72,
        "load_percent": 65,
        "relay_targets": [],
        "dga_status": "normal",
        "comtrade_summary": "inrush_detected",
        "hv_breaker_status": "open",
        "lv_breaker_status": "open",
        "notes": "Buchholz alarm active with otherwise complete evidence."
    }

    response = client.post("/transformer/differential-trip", json=payload)

    assert response.status_code == 200

    data = response.json()
    decision = data["session"]["decisions"][0]
    report = data["session"]["reports"][0]

    assert decision["re_energization_readiness"] == "not_ready"
    assert report["re_energization_readiness"] == "not_ready"

    flags_text = str(decision["asset_condition_readiness"]["asset_condition_flags"]).lower()
    assert "buchholz" in flags_text


def test_asset_condition_high_oil_temperature_forces_not_ready():
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
        "oil_temperature_c": 95,
        "load_percent": 65,
        "relay_targets": [],
        "dga_status": "normal",
        "comtrade_summary": "inrush_detected",
        "hv_breaker_status": "open",
        "lv_breaker_status": "open",
        "notes": "High oil temperature with otherwise complete evidence."
    }

    response = client.post("/transformer/differential-trip", json=payload)

    assert response.status_code == 200

    data = response.json()
    decision = data["session"]["decisions"][0]
    report = data["session"]["reports"][0]

    assert decision["re_energization_readiness"] == "not_ready"
    assert report["re_energization_readiness"] == "not_ready"

    flags_text = str(decision["asset_condition_readiness"]["asset_condition_flags"]).lower()
    assert "oil temperature" in flags_text


def test_asset_condition_clean_case_remains_conditionally_ready():
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
        "relay_targets": [],
        "dga_status": "normal",
        "comtrade_summary": "inrush_detected",
        "hv_breaker_status": "open",
        "lv_breaker_status": "open",
        "notes": "Clean asset condition with complete evidence."
    }

    response = client.post("/transformer/differential-trip", json=payload)

    assert response.status_code == 200

    data = response.json()
    decision = data["session"]["decisions"][0]
    report = data["session"]["reports"][0]

    assert decision["re_energization_readiness"] == "conditionally_ready_for_engineering_review"
    assert report["re_energization_readiness"] == "conditionally_ready_for_engineering_review"
    assert decision["asset_condition_readiness"]["asset_condition_safe"] is True
    assert decision["asset_condition_readiness"]["asset_condition_flags"] == []
