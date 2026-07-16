from pydantic import ValidationError

import pytest

from app.capabilities.errors import (
    CapabilityError,
)


def build_error() -> CapabilityError:
    return CapabilityError(
        error_type="execution_error",
        message="failure",
        capability_id="CAP-TEST-0001",
        request_id="REQ-0001",
        stage="execute",
        retryable=False,
    )


def test_error_model_accepts_valid_values():
    error = build_error()

    assert error.error_type == "execution_error"
    assert error.stage == "execute"
    assert error.retryable is False


def test_error_model_is_frozen():
    error = build_error()

    with pytest.raises(
        ValidationError,
    ):
        error.message = "changed"


def test_error_rejects_unknown_fields():
    payload = build_error().model_dump()
    payload["unknown"] = True

    with pytest.raises(
        ValidationError,
    ):
        CapabilityError(
            **payload,
        )


@pytest.mark.parametrize(
    "stage",
    [
        "validate",
        "execute",
        "audit",
        "runtime",
    ],
)
def test_stage_values(
    stage: str,
):
    error = CapabilityError(
        error_type="execution_error",
        message="failure",
        capability_id="CAP-TEST-0001",
        request_id="REQ-0001",
        stage=stage,
        retryable=False,
    )

    assert error.stage == stage


@pytest.mark.parametrize(
    "invalid_stage",
    [
        "",
        "validation",
        "brain",
        "api",
    ],
)
def test_invalid_stage(
    invalid_stage: str,
):
    payload = build_error().model_dump()
    payload["stage"] = invalid_stage

    with pytest.raises(
        ValidationError,
    ):
        CapabilityError(
            **payload,
        )
