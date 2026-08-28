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
        assert "why_supported" in hypothesis
        assert "why_not_confirmed" in hypothesis
        assert "confidence_drivers" in hypothesis
        assert "confidence_limiters" in hypothesis
        assert "evidence_that_would_change_decision" in hypothesis

        assert isinstance(hypothesis["why_supported"], list)
        assert isinstance(hypothesis["why_not_confirmed"], list)
        assert isinstance(hypothesis["confidence_drivers"], list)
        assert isinstance(hypothesis["confidence_limiters"], list)
        assert isinstance(
            hypothesis["evidence_that_would_change_decision"],
            list,
        )
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

    conflict_description = internal_fault["conflicts"][0]["conflict"]
    recommended_verification = internal_fault["conflicts"][0].get(
        "recommended_verification"
    )

    assert conflict_description in internal_fault["why_not_confirmed"]
    assert conflict_description in internal_fault["confidence_limiters"]

    assert recommended_verification
    assert recommended_verification in internal_fault[
        "evidence_that_would_change_decision"
    ]

    assert conflict_description in internal_fault[
        "conflicting_evidence"
    ]

    assert {
        "limiter_type": "conflicting_evidence",
        "description": conflict_description,
        "severity": "medium",
    } in internal_fault["confidence_limiter_details"]
    conflict_change = next(
        item
        for item in internal_fault["decision_change_details"]
        if item["evidence_type"] == "conflict_verification"
    )

    assert conflict_change["verification_action"] == recommended_verification
    assert conflict_change["observable_condition"] == internal_fault[
        "conflicts"
    ][0]["decision_change_condition"]
    assert conflict_change["severity"] == "medium"
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

    assert evidence_quality["weight_model"] == "metadata_quality_v0.1"
    assert (
        evidence_quality["weight_model_is_calibrated_probability"]
        is False
    )

    weight_details = evidence_quality["evidence_weight_details"]

    assert [
        item["evidence_name"]
        for item in weight_details
    ] == sorted(
        item["evidence_name"]
        for item in weight_details
    )

    relay_weight = next(
        item
        for item in weight_details
        if item["evidence_name"] == "Relay event report"
    )

    assert relay_weight == {
        "evidence_name": "Relay event report",
        "raw_weight": 1.0,
        "metadata_available": True,
        "weight_factors": {
            "verification_factor": 1.0,
            "source_reliability": 1.0,
            "timing_factor": 1.0,
            "freshness_factor": 1.0,
        },
    }

    missing_metadata_weight = next(
        item
        for item in weight_details
        if item["evidence_name"] == "Differential relay targets"
    )

    assert missing_metadata_weight["raw_weight"] == 0.0
    assert missing_metadata_weight["metadata_available"] is False

    assert "freshness_score" in evidence_quality
    assert evidence_quality["freshness_score"] > 0
    assert "Evidence is recent." in evidence_quality["metadata_quality_notes"]

def test_transformer_inrush_explanation_quality():
    evaluations = evaluate_differential_trip_hypotheses(
        available_evidence=[
            "COMTRADE waveform",
        ],
        missing_required_evidence=[
            "Load before trip",
        ],
        buchholz_alarm=False,
        comtrade_available=True,
        dga_available=False,
        oil_temperature_c=72,
        load_percent=None,
        relay_targets=[],
        dga_status="unknown",
        comtrade_summary="inrush_detected",
        hv_breaker_status="unknown",
        lv_breaker_status="unknown",
    )

    inrush = next(
        evaluation
        for evaluation in evaluations
        if evaluation["hypothesis"]
        == "Inrush or abnormal energization condition"
    )

    assert "COMTRADE summary indicates inrush." in inrush["why_supported"]
    assert inrush["confidence_drivers"] == inrush["supporting_evidence"]

    assert "Load before trip" in inrush["why_not_confirmed"]
    assert "Load before trip" in inrush["confidence_limiters"]
    assert "Load before trip" in inrush[
        "evidence_that_would_change_decision"
    ]
    assert inrush["conflicting_evidence"] == []

    assert {
        "limiter_type": "missing_evidence",
        "description": "Load before trip",
    } in inrush["confidence_limiter_details"]

    missing_change = next(
        item
        for item in inrush["decision_change_details"]
        if item["evidence_type"] == "missing_evidence"
        and item["required_evidence"] == "Load before trip"
    )

    assert missing_change["decision_impact"] == (
        "Reviewing this evidence may increase or decrease "
        "confidence in the hypothesis."
    )

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


def test_physics_supported_ct_saturation_adds_support_without_raising_confidence():
    evaluations = evaluate_differential_trip_hypotheses(
        available_evidence=[],
        missing_required_evidence=[],
        relay_targets=[],
        dga_status="not_available",
        comtrade_summary="not_available",
        buchholz_alarm=None,
        comtrade_available=False,
        dga_available=False,
        oil_temperature_c=None,
        load_percent=None,
        physics_ct_saturation_status="supported",
    )

    external = next(
        item
        for item in evaluations
        if item["hypothesis"]
        == "External fault with CT saturation"
    )

    assert (
        "Physics evaluation supports CT saturation."
        in external["supporting_evidence"]
    )

    assert external["confidence"] == "low"


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
    assert decision["re_energization_readiness"] == "safety_lockout"
    assert report["re_energization_readiness"] == "safety_lockout"


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

    assert decision["re_energization_readiness"] == "safety_lockout"
    assert report["re_energization_readiness"] == "safety_lockout"

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


def test_asset_condition_critical_dga_forces_safety_lockout():
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
        "dga_status": "critical",
        "comtrade_summary": "inrush_detected",
        "hv_breaker_status": "open",
        "lv_breaker_status": "open",
        "notes": "Critical DGA with otherwise complete evidence."
    }

    response = client.post("/transformer/differential-trip", json=payload)

    assert response.status_code == 200

    data = response.json()
    decision = data["session"]["decisions"][0]
    report = data["session"]["reports"][0]

    assert decision["re_energization_readiness"] == "safety_lockout"
    assert report["re_energization_readiness"] == "safety_lockout"
    assert decision["asset_condition_readiness"]["safety_lockout_required"] is True

    flags_text = str(decision["asset_condition_readiness"]["asset_condition_flags"]).lower()
    assert "critical" in flags_text
    assert "dga" in flags_text


def test_transformer_api_exposes_explanation_provenance_contract():
    payload = {
        "asset_id": "T1",
        "voltage_level": "230/13.8 kV",
        "event_description": (
            "Transformer tripped by differential relay"
        ),
        "relay_name": "87T",
        "available_data": [
            "Relay event report",
        ],
        "missing_data": [],
        "comtrade_available": False,
        "dga_available": False,
        "buchholz_alarm": None,
        "oil_temperature_c": 72,
        "load_percent": 65,
        "notes": (
            "Initial site inspection and diagnostic review pending."
        ),
    }

    response = client.post(
        "/transformer/differential-trip",
        json=payload,
    )

    assert response.status_code == 200

    data = response.json()
    session = data["session"]

    hypothesis_collections = [
        session["hypotheses"],
        session["reports"][0]["ranked_hypotheses"],
    ]

    for hypotheses in hypothesis_collections:
        assert len(hypotheses) == 5

        for hypothesis in hypotheses:
            assert "explanation_provenance_details" in hypothesis
            assert "explanation_provenance_integrity" in hypothesis

            details = hypothesis[
                "explanation_provenance_details"
            ]
            integrity = hypothesis[
                "explanation_provenance_integrity"
            ]

            assert isinstance(details, list)
            assert isinstance(integrity, dict)

            assert integrity["status"] in {
                "complete",
                "incomplete",
                "not_applicable",
            }
            assert integrity["affects_decision"] is False

            total = integrity["total_statement_count"]
            traceable = integrity["traceable_statement_count"]
            unresolved = integrity["unresolved_statement_count"]

            assert total == len(details)
            assert traceable + unresolved == total

            if total == 0:
                assert integrity["status"] == "not_applicable"
                assert integrity["traceability_ratio"] is None
            else:
                expected_ratio = round(
                    traceable / total,
                    2,
                )
                assert (
                    integrity["traceability_ratio"]
                    == expected_ratio
                )

            for item in details:
                assert "field" in item
                assert "statement" in item
                assert "statement_index" in item
                assert "source_type" in item
                assert "source_field" in item
                assert "source_index" in item
                assert "source_path" in item
                assert "traceable" in item


def test_transformer_api_exposes_hypothesis_ranking_audit():
    payload = {
        "asset_id": "T1",
        "voltage_level": "230/13.8 kV",
        "event_description": (
            "Transformer tripped by differential relay"
        ),
        "relay_name": "87T",
        "available_data": [
            "Relay event report",
        ],
        "missing_data": [],
        "comtrade_available": False,
        "dga_available": False,
        "buchholz_alarm": None,
        "oil_temperature_c": 72,
        "load_percent": 65,
        "notes": "Initial engineering review pending.",
    }

    response = client.post(
        "/transformer/differential-trip",
        json=payload,
    )

    assert response.status_code == 200

    session = response.json()["session"]
    session_hypotheses = session["hypotheses"]
    ranked_hypotheses = session["reports"][0][
        "ranked_hypotheses"
    ]
    top_ranked = session["decisions"][0][
        "top_ranked_hypothesis"
    ]

    assert len(session_hypotheses) == len(ranked_hypotheses)
    assert top_ranked["ranking_audit"]["rank_position"] == 1

    for expected_rank, hypothesis in enumerate(
        ranked_hypotheses,
        start=1,
    ):
        audit = hypothesis["ranking_audit"]

        assert audit["rank_position"] == expected_rank
        assert audit["original_position"] >= 1
        assert audit["confidence"] == hypothesis["confidence"]
        assert audit["confidence_rank"] in {1, 2, 3}

        assert audit["supporting_evidence_count"] == len(
            hypothesis["supporting_evidence"]
        )
        assert audit["missing_evidence_count"] == len(
            hypothesis["missing_evidence"]
        )
        assert audit["conflict_count"] == len(
            hypothesis["conflicts"]
        )

        assert audit["ranking_key"] == [
            audit["confidence_rank"],
            audit["supporting_evidence_count"],
            -audit["missing_evidence_count"],
            -audit["conflict_count"],
        ]
        assert audit["tie_breaker_policy"] == "stable_input_order"
        assert audit["ranking_algorithm"] == (
            "confidence_support_missing_conflict_v0.1"
        )
        assert audit["affects_ranking"] is False
        assert audit["ranking_algorithm_changed"] is False

    for hypothesis in session_hypotheses:
        assert "ranking_audit" in hypothesis


def test_transformer_api_rejects_duplicate_evidence_metadata_names():
    payload = {
        "available_data": [
            "Relay event report",
        ],
        "evidence_metadata": [
            {
                "evidence_name": "Relay event report",
                "source_type": "relay",
                "timestamp_relation": "during_event",
                "evidence_age_days": 1,
                "verified": True,
            },
            {
                "evidence_name": "Relay event report",
                "source_type": "relay",
                "timestamp_relation": "during_event",
                "evidence_age_days": 1,
                "verified": True,
            },
        ],
    }

    response = client.post(
        "/transformer/differential-trip",
        json=payload,
    )

    assert response.status_code == 422
    assert "unique evidence_name" in response.text


def test_transformer_api_rejects_oversized_collection_inputs():
    oversized = [
        f"Evidence item {index}"
        for index in range(101)
    ]

    for field_name in (
        "available_data",
        "missing_data",
        "relay_targets",
    ):
        response = client.post(
            "/transformer/differential-trip",
            json={
                field_name: oversized,
            },
        )

        assert response.status_code == 422


def test_transformer_api_rejects_oversized_evidence_metadata():
    available_data = [
        "Available evidence",
    ]
    missing_data = [
        f"Missing evidence {index}"
        for index in range(100)
    ]
    evidence_names = available_data + missing_data

    evidence_metadata = [
        {
            "evidence_name": evidence_name,
            "source_type": "unknown",
            "timestamp_relation": "unknown",
            "evidence_age_days": 0,
            "verified": False,
        }
        for evidence_name in evidence_names
    ]

    response = client.post(
        "/transformer/differential-trip",
        json={
            "available_data": available_data,
            "missing_data": missing_data,
            "evidence_metadata": evidence_metadata,
        },
    )

    assert len(available_data) <= 100
    assert len(missing_data) <= 100
    assert len(evidence_metadata) == 101
    assert response.status_code == 422


def test_transformer_api_rejects_oversized_text_inputs():
    cases = {
        "asset_id": "A" * 201,
        "voltage_level": "V" * 201,
        "event_description": "E" * 2001,
        "relay_name": "R" * 201,
        "notes": "N" * 5001,
    }

    for field_name, value in cases.items():
        response = client.post(
            "/transformer/differential-trip",
            json={
                field_name: value,
            },
        )

        assert response.status_code == 422


def test_transformer_api_rejects_oversized_evidence_item_text():
    response = client.post(
        "/transformer/differential-trip",
        json={
            "available_data": [
                "E" * 501,
            ],
        },
    )

    assert response.status_code == 422


def test_transformer_api_exposes_confidence_calibration_audit():
    payload = {
        "asset_id": "T1",
        "voltage_level": "230/13.8 kV",
        "event_description": (
            "Transformer tripped by differential relay"
        ),
        "available_data": [
            "Relay event report",
            "COMTRADE waveform",
        ],
        "missing_data": [],
    }

    response = client.post(
        "/transformer/differential-trip",
        json=payload,
    )

    assert response.status_code == 200

    data = response.json()

    hypotheses = data["session"]["hypotheses"]

    assert hypotheses

    for hypothesis in hypotheses:
        audit = hypothesis["confidence_calibration"]

        assert audit["confidence"] == hypothesis["confidence"]
        assert audit["confidence_type"] == "qualitative"
        assert audit["is_calibrated_probability"] is False
        assert audit["calibrated_probability"] is None
        assert audit["affects_confidence"] is False
        assert audit["affects_ranking"] is False
        assert audit["affects_decision"] is False


def test_transformer_api_exposes_reasoning_trace_audit():
    payload = {
        "asset_id": "T1",
        "voltage_level": "230/13.8 kV",
        "event_description": (
            "Transformer tripped by differential relay"
        ),
        "available_data": [
            "Relay event report",
            "COMTRADE waveform",
        ],
        "missing_data": [],
    }

    response = client.post(
        "/transformer/differential-trip",
        json=payload,
    )

    assert response.status_code == 200

    session = response.json()["session"]
    audit = session["metadata"]["reasoning_trace_audit"]

    assert audit["status"] == "complete"
    assert audit["trace_complete"] is True
    assert audit["order_valid"] is True

    assert audit["missing_stages"] == []
    assert audit["duplicate_stages"] == []
    assert audit["unknown_stages"] == []

    assert audit["affects_confidence"] is False
    assert audit["affects_ranking"] is False
    assert audit["affects_decision"] is False


def test_transformer_api_exposes_shadow_physics_observations():
    payload = {
        "asset_id": "T1",
        "voltage_level": "230/13.8 kV",
        "event_description": (
            "Transformer tripped by differential relay"
        ),
        "available_data": [
            "Relay event report",
            "COMTRADE waveform",
        ],
        "missing_data": [],
        "physics_measurements": {
            "hv_currents": {
                "phase_a": 100.0,
                "phase_b": 100.0,
                "phase_c": 100.0,
            },
            "lv_currents": {
                "phase_a": 1000.0,
                "phase_b": 1000.0,
                "phase_c": 1000.0,
            },
            "hv_ct_ratio": {
                "primary_a": 200.0,
                "secondary_a": 1.0,
            },
            "lv_ct_ratio": {
                "primary_a": 2000.0,
                "secondary_a": 1.0,
            },
            "hv_nominal_voltage_kv": 230.0,
            "lv_nominal_voltage_kv": 13.8,
        },
        "physics_context": {
            "vector_group": "Dyn11",
            "vector_group_compensation_applied": True,
        },
        "harmonic_measurement": {
            "fundamental_a": 100.0,
            "second_harmonic_a": 20.0,
            "fifth_harmonic_a": 5.0,
        },
    }

    response = client.post(
        "/transformer/differential-trip",
        json=payload,
    )

    assert response.status_code == 200

    data = response.json()
    observations = data["session"]["observations"]

    physics_observations = [
        item
        for item in observations
        if item.get("source") == "transformer_physics"
    ]

    assert len(physics_observations) == 2

    observation_types = {
        item["observation_type"]
        for item in physics_observations
    }

    assert "differential_current" in observation_types
    assert "harmonic_restraint" in observation_types

    for item in physics_observations:
        assert item["affects_confidence"] is False
        assert item["affects_ranking"] is False
        assert item["affects_decision"] is False


def test_transformer_api_exposes_evidence_relationship_validation():
    payload = {
        "asset_id": "T1",
        "voltage_level": "230/13.8 kV",
        "event_description": (
            "Transformer tripped by differential relay"
        ),
        "available_data": [
            "Relay event report",
            "COMTRADE waveform",
        ],
        "missing_data": [],
        "physics_measurements": {
            "hv_currents": {
                "phase_a": 100.0,
                "phase_b": 100.0,
                "phase_c": 100.0,
            },
            "lv_currents": {
                "phase_a": 1000.0,
                "phase_b": 1000.0,
                "phase_c": 1000.0,
            },
            "hv_ct_ratio": {
                "primary_a": 200.0,
                "secondary_a": 1.0,
            },
            "lv_ct_ratio": {
                "primary_a": 2000.0,
                "secondary_a": 1.0,
            },
            "hv_nominal_voltage_kv": 230.0,
            "lv_nominal_voltage_kv": 13.8,
        },
        "physics_context": {
            "vector_group": "Dyn11",
            "vector_group_compensation_applied": True,
        },
        "harmonic_measurement": {
            "fundamental_a": 100.0,
            "second_harmonic_a": 20.0,
            "fifth_harmonic_a": 5.0,
        },
    }

    response = client.post(
        "/transformer/differential-trip",
        json=payload,
    )

    assert response.status_code == 200

    metadata = response.json()["session"]["metadata"]

    validation = metadata[
        "evidence_relationship_validation"
    ]

    assert validation["valid"] is True
    assert validation["missing_targets"] == []
    assert validation["self_references"] == []
    assert validation["duplicate_relationships"] == []
    assert validation["affects_reasoning"] is False
    assert validation["affects_decision"] is False


def test_transformer_api_exposes_differential_characteristic_observation():
    payload = {
        "asset_id": "T1",
        "voltage_level": "230/13.8 kV",
        "event_description": (
            "Transformer tripped by differential relay"
        ),
        "available_data": [
            "Relay event report",
            "COMTRADE waveform",
        ],
        "missing_data": [],
        "physics_measurements": {
            "hv_currents": {
                "phase_a": 100.0,
                "phase_b": 100.0,
                "phase_c": 100.0,
            },
            "lv_currents": {
                "phase_a": 1000.0,
                "phase_b": 1000.0,
                "phase_c": 1000.0,
            },
            "hv_ct_ratio": {
                "primary_a": 200.0,
                "secondary_a": 1.0,
            },
            "lv_ct_ratio": {
                "primary_a": 2000.0,
                "secondary_a": 1.0,
            },
            "hv_nominal_voltage_kv": 230.0,
            "lv_nominal_voltage_kv": 13.8,
        },
        "physics_context": {
            "vector_group": "Dyn11",
            "vector_group_compensation_applied": True,
        },
        "differential_characteristic_settings": {
            "pickup_a": 0.30,
            "slope": 0.25,
        },
    }

    response = client.post(
        "/transformer/differential-trip",
        json=payload,
    )

    assert response.status_code == 200

    observations = response.json()["session"]["observations"]

    characteristic = next(
        item
        for item in observations
        if item.get("observation_type")
        == "differential_characteristic"
    )

    assert characteristic["validity_status"] == "valid"
    assert (
        characteristic["data"]["affects_decision"]
        is False
    )


def test_differential_characteristic_not_emitted_without_settings():
    payload = {
        "asset_id": "T1",
        "event_description": (
            "Transformer differential trip"
        ),
    }

    response = client.post(
        "/transformer/differential-trip",
        json=payload,
    )

    assert response.status_code == 200

    observations = response.json()["session"]["observations"]

    assert not any(
        item.get("observation_type")
        == "differential_characteristic"
        for item in observations
    )


def test_transformer_api_exposes_ct_saturation_observation():
    payload = {
        "asset_id": "T1",
        "event_description": (
            "Transformer differential trip"
        ),
        "ct_saturation_indicators": {
            "waveform_asymmetry_detected": True,
            "secondary_current_distortion_detected": True,
            "high_through_fault_current_detected": True,
        },
    }

    response = client.post(
        "/transformer/differential-trip",
        json=payload,
    )

    assert response.status_code == 200

    observations = response.json()[
        "session"
    ]["observations"]

    observation = next(
        item
        for item in observations
        if item.get("observation_type")
        == "ct_saturation_evaluation"
    )

    assert observation["validity_status"] == "valid"
    assert observation["data"]["status"] == "supported"
    assert observation["data"]["shadow_only"] is True
    assert (
        observation["data"]["affects_reasoning"]
        is False
    )
    assert (
        observation["data"]["affects_decision"]
        is False
    )


def test_ct_saturation_observation_not_emitted_without_indicators():
    payload = {
        "asset_id": "T1",
        "event_description": (
            "Transformer differential trip"
        ),
    }

    response = client.post(
        "/transformer/differential-trip",
        json=payload,
    )

    assert response.status_code == 200

    observations = response.json()[
        "session"
    ]["observations"]

    assert not any(
        item.get("observation_type")
        == "ct_saturation_evaluation"
        for item in observations
    )


def test_ct_saturation_observation_is_exposed_as_engineering_evidence():
    payload = {
        "asset_id": "T1",
        "event_description": (
            "Transformer differential trip"
        ),
        "ct_saturation_indicators": {
            "waveform_asymmetry_detected": True,
            "secondary_current_distortion_detected": True,
            "high_through_fault_current_detected": True,
        },
    }

    response = client.post(
        "/transformer/differential-trip",
        json=payload,
    )

    assert response.status_code == 200

    evidence = response.json()["session"]["evidence"]

    item = next(
        evidence_item
        for evidence_item in evidence
        if evidence_item.get("evidence_id")
        == "physics:ct_saturation_evaluation"
    )

    assert item["evidence_type"] == (
        "ct_saturation_evaluation"
    )
    assert item["category"] == "physics"

    assert item["value"]["status"] == "supported"
    assert item["value"]["confirmed"] is False

    assert item["affects_reasoning"] is False


def test_ct_saturation_evidence_not_emitted_without_indicators():
    payload = {
        "asset_id": "T1",
        "event_description": (
            "Transformer differential trip"
        ),
    }

    response = client.post(
        "/transformer/differential-trip",
        json=payload,
    )

    assert response.status_code == 200

    evidence = response.json()["session"]["evidence"]

    assert not any(
        item.get("evidence_id")
        == "physics:ct_saturation_evaluation"
        for item in evidence
    )


def test_ct_saturation_evidence_is_present_in_evidence_graph():
    payload = {
        "asset_id": "T1",
        "event_description": (
            "Transformer differential trip"
        ),
        "ct_saturation_indicators": {
            "waveform_asymmetry_detected": True,
            "secondary_current_distortion_detected": True,
            "high_through_fault_current_detected": True,
        },
    }

    response = client.post(
        "/transformer/differential-trip",
        json=payload,
    )

    assert response.status_code == 200

    graph = response.json()["session"][
        "evidence_graph"
    ]

    node = next(
        item
        for item in graph["nodes"]
        if item["evidence_id"]
        == "physics:ct_saturation_evaluation"
    )

    assert node["evidence_type"] == (
        "ct_saturation_evaluation"
    )


def test_api_ct_saturation_physics_support_reaches_external_hypothesis():
    payload = {
        "asset_id": "T1",
        "event_description": (
            "Transformer differential trip"
        ),
        "ct_saturation_indicators": {
            "waveform_asymmetry_detected": True,
            "secondary_current_distortion_detected": True,
            "high_through_fault_current_detected": True,
        },
        "comtrade_summary": "not_available",
    }

    response = client.post(
        "/transformer/differential-trip",
        json=payload,
    )

    assert response.status_code == 200

    hypotheses = response.json()["session"]["hypotheses"]

    external = next(
        item
        for item in hypotheses
        if item["hypothesis"]
        == "External fault with CT saturation"
    )

    assert (
        "Physics evaluation supports CT saturation."
        in external["supporting_evidence"]
    )

    assert external["confidence"] == "low"


def test_api_exposes_external_fault_discrimination_observation():
    payload = {
        "asset_id": "T1",
        "voltage_level": "230/13.8 kV",
        "event_description": (
            "Transformer tripped by differential relay"
        ),
        "available_data": [
            "Relay event report",
            "COMTRADE waveform",
        ],
        "missing_data": [],
        "physics_measurements": {
            "hv_currents": {
                "phase_a": 100.0,
                "phase_b": 100.0,
                "phase_c": 100.0,
            },
            "lv_currents": {
                "phase_a": 1000.0,
                "phase_b": 1000.0,
                "phase_c": 1000.0,
            },
            "hv_ct_ratio": {
                "primary_a": 200.0,
                "secondary_a": 1.0,
            },
            "lv_ct_ratio": {
                "primary_a": 2000.0,
                "secondary_a": 1.0,
            },
            "hv_nominal_voltage_kv": 230.0,
            "lv_nominal_voltage_kv": 13.8,
        },
        "physics_context": {
            "vector_group": "Dyn11",
            "vector_group_compensation_applied": True,
        },
        "differential_characteristic_settings": {
            "pickup_a": 0.30,
            "slope": 0.25,
        },
        "ct_saturation_indicators": {
            "waveform_asymmetry_detected": True,
            "secondary_current_distortion_detected": True,
            "high_through_fault_current_detected": True,
        },
    }

    response = client.post(
        "/transformer/differential-trip",
        json=payload,
    )

    assert response.status_code == 200

    observations = response.json()[
        "session"
    ]["observations"]

    observation = next(
        item
        for item in observations
        if item.get("observation_type")
        == "external_fault_discrimination"
    )

    assert observation["validity_status"] == "valid"
    assert observation["data"]["status"] == "supported"
    assert observation["data"]["confirmed"] is False
    assert observation["data"]["shadow_only"] is True
    assert (
        observation["data"]["affects_reasoning"]
        is False
    )
    assert (
        observation["data"]["affects_decision"]
        is False
    )


def test_external_fault_discrimination_not_emitted_without_operating_region():
    payload = {
        "asset_id": "T1",
        "event_description": (
            "Transformer differential trip"
        ),
        "ct_saturation_indicators": {
            "waveform_asymmetry_detected": True,
            "secondary_current_distortion_detected": True,
            "high_through_fault_current_detected": True,
        },
    }

    response = client.post(
        "/transformer/differential-trip",
        json=payload,
    )

    assert response.status_code == 200

    observations = response.json()[
        "session"
    ]["observations"]

    assert not any(
        item.get("observation_type")
        == "external_fault_discrimination"
        for item in observations
    )


def test_external_fault_discrimination_is_exposed_as_engineering_evidence():
    payload = {
        "asset_id": "T1",
        "event_description": (
            "Transformer differential trip"
        ),
        "physics_measurements": {
            "hv_currents": {
                "phase_a": 100.0,
                "phase_b": 100.0,
                "phase_c": 100.0,
            },
            "lv_currents": {
                "phase_a": 1000.0,
                "phase_b": 1000.0,
                "phase_c": 1000.0,
            },
            "hv_ct_ratio": {
                "primary_a": 200.0,
                "secondary_a": 1.0,
            },
            "lv_ct_ratio": {
                "primary_a": 2000.0,
                "secondary_a": 1.0,
            },
            "hv_nominal_voltage_kv": 230.0,
            "lv_nominal_voltage_kv": 13.8,
        },
        "physics_context": {
            "vector_group": "Dyn11",
            "vector_group_compensation_applied": True,
        },
        "differential_characteristic_settings": {
            "pickup_a": 0.30,
            "slope": 0.25,
        },
        "ct_saturation_indicators": {
            "waveform_asymmetry_detected": True,
            "secondary_current_distortion_detected": True,
            "high_through_fault_current_detected": True,
        },
    }

    response = client.post(
        "/transformer/differential-trip",
        json=payload,
    )

    assert response.status_code == 200

    evidence = response.json()["session"]["evidence"]

    item = next(
        entry
        for entry in evidence
        if entry.get("evidence_id")
        == "physics:external_fault_discrimination"
    )

    assert item["category"] == "physics"
    assert item["value"]["status"] == "supported"
    assert item["value"]["confirmed"] is False
    assert item["affects_reasoning"] is False


def test_external_fault_discrimination_evidence_enters_evidence_graph():
    payload = {
        "asset_id": "T1",
        "event_description": (
            "Transformer differential trip"
        ),
        "physics_measurements": {
            "hv_currents": {
                "phase_a": 100.0,
                "phase_b": 100.0,
                "phase_c": 100.0,
            },
            "lv_currents": {
                "phase_a": 1000.0,
                "phase_b": 1000.0,
                "phase_c": 1000.0,
            },
            "hv_ct_ratio": {
                "primary_a": 200.0,
                "secondary_a": 1.0,
            },
            "lv_ct_ratio": {
                "primary_a": 2000.0,
                "secondary_a": 1.0,
            },
            "hv_nominal_voltage_kv": 230.0,
            "lv_nominal_voltage_kv": 13.8,
        },
        "physics_context": {
            "vector_group": "Dyn11",
            "vector_group_compensation_applied": True,
        },
        "differential_characteristic_settings": {
            "pickup_a": 0.30,
            "slope": 0.25,
        },
        "ct_saturation_indicators": {
            "waveform_asymmetry_detected": True,
            "secondary_current_distortion_detected": True,
            "high_through_fault_current_detected": True,
        },
    }

    response = client.post(
        "/transformer/differential-trip",
        json=payload,
    )

    graph = response.json()["session"]["evidence_graph"]

    node = next(
        item
        for item in graph["nodes"]
        if item["evidence_id"]
        == "physics:external_fault_discrimination"
    )

    assert node["evidence_type"] == (
        "external_fault_discrimination"
    )


def test_external_fault_discrimination_evidence_traces_derivation_sources():
    payload = {
        "asset_id": "T1",
        "event_description": (
            "Transformer differential trip"
        ),
        "physics_measurements": {
            "hv_currents": {
                "phase_a": 100.0,
                "phase_b": 100.0,
                "phase_c": 100.0,
            },
            "lv_currents": {
                "phase_a": 1000.0,
                "phase_b": 1000.0,
                "phase_c": 1000.0,
            },
            "hv_ct_ratio": {
                "primary_a": 200.0,
                "secondary_a": 1.0,
            },
            "lv_ct_ratio": {
                "primary_a": 2000.0,
                "secondary_a": 1.0,
            },
            "hv_nominal_voltage_kv": 230.0,
            "lv_nominal_voltage_kv": 13.8,
        },
        "physics_context": {
            "vector_group": "Dyn11",
            "vector_group_compensation_applied": True,
        },
        "differential_characteristic_settings": {
            "pickup_a": 0.30,
            "slope": 0.25,
        },
        "ct_saturation_indicators": {
            "waveform_asymmetry_detected": True,
            "secondary_current_distortion_detected": True,
            "high_through_fault_current_detected": True,
        },
    }

    response = client.post(
        "/transformer/differential-trip",
        json=payload,
    )

    assert response.status_code == 200

    evidence = response.json()["session"]["evidence"]

    item = next(
        entry
        for entry in evidence
        if entry["evidence_id"]
        == "physics:external_fault_discrimination"
    )

    relationships = item["relationships"]

    identities = {
        (
            relation["target_evidence_id"],
            relation["relation"],
        )
        for relation in relationships
    }

    assert (
        "physics:differential_characteristic",
        "derived_from",
    ) in identities

    assert (
        "physics:ct_saturation_evaluation",
        "derived_from",
    ) in identities


def test_api_exposes_through_fault_observation():
    payload = {
        "asset_id": "T1",
        "event_description": (
            "Transformer differential trip"
        ),
        "through_fault_context": {
            "upstream_protection_operated": True,
            "downstream_protection_operated": True,
            "transformer_breakers_opened": True,
            "high_through_fault_current_detected": True,
        },
    }

    response = client.post(
        "/transformer/differential-trip",
        json=payload,
    )

    assert response.status_code == 200

    observations = response.json()[
        "session"
    ]["observations"]

    observation = next(
        item
        for item in observations
        if item.get("observation_type")
        == "through_fault_evaluation"
    )

    assert observation["validity_status"] == "valid"
    assert observation["data"]["status"] == "supported"
    assert observation["data"]["confirmed"] is False
    assert observation["data"]["shadow_only"] is True
    assert observation["data"]["affects_reasoning"] is False
    assert observation["data"]["affects_decision"] is False


def test_through_fault_observation_not_emitted_without_context():
    payload = {
        "asset_id": "T1",
        "event_description": (
            "Transformer differential trip"
        ),
    }

    response = client.post(
        "/transformer/differential-trip",
        json=payload,
    )

    assert response.status_code == 200

    observations = response.json()[
        "session"
    ]["observations"]

    assert not any(
        item.get("observation_type")
        == "through_fault_evaluation"
        for item in observations
    )


def test_through_fault_observation_is_exposed_as_engineering_evidence():
    payload = {
        "asset_id": "T1",
        "event_description": (
            "Transformer differential trip"
        ),
        "through_fault_context": {
            "upstream_protection_operated": True,
            "downstream_protection_operated": True,
            "transformer_breakers_opened": True,
            "high_through_fault_current_detected": True,
        },
    }

    response = client.post(
        "/transformer/differential-trip",
        json=payload,
    )

    assert response.status_code == 200

    evidence = response.json()["session"]["evidence"]

    item = next(
        entry
        for entry in evidence
        if entry.get("evidence_id")
        == "physics:through_fault_evaluation"
    )

    assert item["evidence_type"] == "through_fault_evaluation"
    assert item["category"] == "physics"
    assert item["value"]["status"] == "supported"
    assert item["value"]["confirmed"] is False
    assert item["affects_reasoning"] is False


def test_through_fault_evidence_enters_evidence_graph():
    payload = {
        "asset_id": "T1",
        "event_description": (
            "Transformer differential trip"
        ),
        "through_fault_context": {
            "upstream_protection_operated": True,
            "downstream_protection_operated": True,
            "transformer_breakers_opened": True,
            "high_through_fault_current_detected": True,
        },
    }

    response = client.post(
        "/transformer/differential-trip",
        json=payload,
    )

    assert response.status_code == 200

    graph = response.json()["session"]["evidence_graph"]

    node = next(
        item
        for item in graph["nodes"]
        if item["evidence_id"]
        == "physics:through_fault_evaluation"
    )

    assert node["evidence_type"] == "through_fault_evaluation"


def test_external_fault_discrimination_provenance_includes_through_fault_evidence():
    payload = {
        "asset_id": "T1",
        "event_description": (
            "Transformer differential trip"
        ),
        "physics_measurements": {
            "hv_currents": {
                "phase_a": 100.0,
                "phase_b": 100.0,
                "phase_c": 100.0,
            },
            "lv_currents": {
                "phase_a": 1000.0,
                "phase_b": 1000.0,
                "phase_c": 1000.0,
            },
            "hv_ct_ratio": {
                "primary_a": 200.0,
                "secondary_a": 1.0,
            },
            "lv_ct_ratio": {
                "primary_a": 2000.0,
                "secondary_a": 1.0,
            },
            "hv_nominal_voltage_kv": 230.0,
            "lv_nominal_voltage_kv": 13.8,
        },
        "physics_context": {
            "vector_group": "Dyn11",
            "vector_group_compensation_applied": True,
        },
        "differential_characteristic_settings": {
            "pickup_a": 0.30,
            "slope": 0.25,
        },
        "ct_saturation_indicators": {
            "waveform_asymmetry_detected": True,
            "secondary_current_distortion_detected": True,
            "high_through_fault_current_detected": True,
        },
        "through_fault_context": {
            "upstream_protection_operated": True,
            "downstream_protection_operated": True,
            "transformer_breakers_opened": True,
            "high_through_fault_current_detected": True,
        },
    }

    response = client.post(
        "/transformer/differential-trip",
        json=payload,
    )

    assert response.status_code == 200

    evidence = response.json()["session"]["evidence"]

    item = next(
        entry
        for entry in evidence
        if entry["evidence_id"]
        == "physics:external_fault_discrimination"
    )

    identities = {
        (
            relation["target_evidence_id"],
            relation["relation"],
        )
        for relation in item["relationships"]
    }

    assert (
        "physics:through_fault_evaluation",
        "derived_from",
    ) in identities


def test_external_fault_provenance_omits_through_fault_when_context_missing():
    payload = {
        "asset_id": "T1",
        "event_description": "Transformer differential trip",
        "physics_measurements": {
            "hv_currents": {
                "phase_a": 100.0,
                "phase_b": 100.0,
                "phase_c": 100.0,
            },
            "lv_currents": {
                "phase_a": 1000.0,
                "phase_b": 1000.0,
                "phase_c": 1000.0,
            },
            "hv_ct_ratio": {
                "primary_a": 200.0,
                "secondary_a": 1.0,
            },
            "lv_ct_ratio": {
                "primary_a": 2000.0,
                "secondary_a": 1.0,
            },
            "hv_nominal_voltage_kv": 230.0,
            "lv_nominal_voltage_kv": 13.8,
        },
        "physics_context": {
            "vector_group": "Dyn11",
            "vector_group_compensation_applied": True,
        },
        "differential_characteristic_settings": {
            "pickup_a": 0.30,
            "slope": 0.25,
        },
        "ct_saturation_indicators": {
            "waveform_asymmetry_detected": True,
            "secondary_current_distortion_detected": True,
            "high_through_fault_current_detected": True,
        },
    }

    response = client.post(
        "/transformer/differential-trip",
        json=payload,
    )

    assert response.status_code == 200

    evidence = response.json()["session"]["evidence"]

    external = next(
        item
        for item in evidence
        if item["evidence_id"]
        == "physics:external_fault_discrimination"
    )

    targets = {
        relation["target_evidence_id"]
        for relation in external["relationships"]
    }

    assert "physics:differential_characteristic" in targets
    assert "physics:ct_saturation_evaluation" in targets
    assert "physics:through_fault_evaluation" not in targets


def test_external_fault_provenance_targets_exist_in_session_evidence():
    payload = {
        "asset_id": "T1",
        "event_description": "Transformer differential trip",
        "physics_measurements": {
            "hv_currents": {
                "phase_a": 100.0,
                "phase_b": 100.0,
                "phase_c": 100.0,
            },
            "lv_currents": {
                "phase_a": 1000.0,
                "phase_b": 1000.0,
                "phase_c": 1000.0,
            },
            "hv_ct_ratio": {
                "primary_a": 200.0,
                "secondary_a": 1.0,
            },
            "lv_ct_ratio": {
                "primary_a": 2000.0,
                "secondary_a": 1.0,
            },
            "hv_nominal_voltage_kv": 230.0,
            "lv_nominal_voltage_kv": 13.8,
        },
        "physics_context": {
            "vector_group": "Dyn11",
            "vector_group_compensation_applied": True,
        },
        "differential_characteristic_settings": {
            "pickup_a": 0.30,
            "slope": 0.25,
        },
        "ct_saturation_indicators": {
            "waveform_asymmetry_detected": True,
            "secondary_current_distortion_detected": True,
            "high_through_fault_current_detected": True,
        },
        "through_fault_context": {
            "upstream_protection_operated": True,
            "downstream_protection_operated": True,
            "transformer_breakers_opened": True,
            "high_through_fault_current_detected": True,
        },
    }

    response = client.post(
        "/transformer/differential-trip",
        json=payload,
    )

    assert response.status_code == 200

    session = response.json()["session"]
    evidence = session["evidence"]

    evidence_ids = {
        item["evidence_id"]
        for item in evidence
    }

    external = next(
        item
        for item in evidence
        if item["evidence_id"]
        == "physics:external_fault_discrimination"
    )

    derived_from_targets = {
        relation["target_evidence_id"]
        for relation in external["relationships"]
        if relation["relation"] == "derived_from"
    }

    assert derived_from_targets
    assert derived_from_targets <= evidence_ids

def test_external_fault_discrimination_adds_reasoning_support_without_raising_confidence():
    evaluations = evaluate_differential_trip_hypotheses(
        available_evidence=[],
        missing_required_evidence=[],
        relay_targets=[],
        dga_status="not_available",
        comtrade_summary="not_available",
        buchholz_alarm=None,
        comtrade_available=False,
        dga_available=False,
        oil_temperature_c=None,
        load_percent=None,
        physics_external_fault_discrimination_status=(
            "supported"
        ),
    )

    external = next(
        item
        for item in evaluations
        if item["hypothesis"]
        == "External fault with CT saturation"
    )

    assert (
        "Physics discrimination supports an external "
        "fault with CT saturation scenario."
        in external["supporting_evidence"]
    )

    assert external["confidence"] == "low"