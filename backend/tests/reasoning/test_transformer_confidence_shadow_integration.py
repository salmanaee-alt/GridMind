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


def test_transformer_exposes_confidence_shadow_metadata():
    response = client.post(
        "/transformer/differential-trip",
        json=build_request(),
    )

    assert response.status_code == 200

    session = response.json()["session"]

    assert (
        "confidence_propagation"
        in session["metadata"]
    )


def test_confidence_integration_is_shadow_only():
    response = client.post(
        "/transformer/differential-trip",
        json=build_request(),
    )

    confidence = (
        response.json()["session"]["metadata"][
            "confidence_propagation"
        ]
    )

    assert confidence["shadow_only"] is True
    assert confidence["affects_reasoning"] is False
    assert confidence["affects_decision"] is False


def test_confidence_integration_uses_no_invented_seed_scores():
    response = client.post(
        "/transformer/differential-trip",
        json=build_request(),
    )

    confidence = (
        response.json()["session"]["metadata"][
            "confidence_propagation"
        ]
    )

    assert (
        confidence["input_confidence_scores"]
        == {}
    )


def test_confidence_integration_serializes_engine_result():
    response = client.post(
        "/transformer/differential-trip",
        json=build_request(),
    )

    confidence = (
        response.json()["session"]["metadata"][
            "confidence_propagation"
        ]
    )

    assert "result" in confidence
    assert confidence["result"]["status"] in {
        "success",
        "skipped",
    }


def test_confidence_shadow_does_not_change_existing_hypotheses():
    response = client.post(
        "/transformer/differential-trip",
        json=build_request(),
    )

    session = response.json()["session"]

    confidence = session["metadata"][
        "confidence_propagation"
    ]

    assert confidence["affects_reasoning"] is False
    assert confidence["affects_decision"] is False


def test_brain_preserves_confidence_propagation_metadata():
    response = client.post(
        "/transformer/differential-trip",
        json=build_request(),
    )

    session = response.json()["session"]

    confidence = session["metadata"][
        "confidence_propagation"
    ]

    assert confidence["shadow_only"] is True
    assert confidence["affects_reasoning"] is False
    assert confidence["affects_decision"] is False
    assert confidence["input_confidence_scores"] == {}