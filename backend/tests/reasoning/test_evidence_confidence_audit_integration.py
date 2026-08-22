from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def build_request():
    return {
        "asset_id": "T1",
        "event_description": (
            "Transformer differential trip"
        ),
        "available_data": [],
    }


def test_transformer_exposes_evidence_confidence_audit():
    response = client.post(
        "/transformer/differential-trip",
        json=build_request(),
    )

    assert response.status_code == 200

    session = response.json()["session"]

    assert (
        "evidence_confidence_audit"
        in session["metadata"]
    )


def test_evidence_confidence_audit_is_shadow_only():
    response = client.post(
        "/transformer/differential-trip",
        json=build_request(),
    )

    audit = (
        response.json()["session"]["metadata"][
            "evidence_confidence_audit"
        ]
    )

    assert audit["shadow_only"] is True
    assert audit["affects_reasoning"] is False
    assert audit["affects_decision"] is False


def test_evidence_confidence_audit_never_exposes_calibrated_probability():
    response = client.post(
        "/transformer/differential-trip",
        json=build_request(),
    )

    audit = (
        response.json()["session"]["metadata"][
            "evidence_confidence_audit"
        ]
    )

    for assessment in audit["assessments"]:
        assert (
            assessment["is_calibrated_probability"]
            is False
        )
        assert (
            assessment["calibrated_probability"]
            is None
        )
        assert (
            assessment["usable_as_propagation_seed"]
            is False
        )


def test_evidence_confidence_audit_preserves_evidence_ids():
    response = client.post(
        "/transformer/differential-trip",
        json=build_request(),
    )

    session = response.json()["session"]

    evidence_ids = {
        item["evidence_id"]
        for item in session["evidence"]
    }

    audit_ids = {
        item["evidence_id"]
        for item in session["metadata"][
            "evidence_confidence_audit"
        ]["assessments"]
    }

    assert audit_ids == evidence_ids


def test_evidence_confidence_audit_does_not_feed_propagation_seeds():
    response = client.post(
        "/transformer/differential-trip",
        json=build_request(),
    )

    metadata = (
        response.json()["session"]["metadata"]
    )

    assert (
        metadata["confidence_propagation"][
            "input_confidence_scores"
        ]
        == {}
    )