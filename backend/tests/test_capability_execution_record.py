from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.capabilities.contracts import (
    CapabilityExecutionRecord,
)


def test_valid_execution_record():
    record = CapabilityExecutionRecord(
        capability_id="CAP-TEST-0001",
        status="success",
        execution_mode="shadow",
        affects_decision=False,
        duration_ms=12.5,
        error=None,
    )

    assert record.capability_id == "CAP-TEST-0001"
    assert record.status == "success"


def test_negative_duration_rejected():
    with pytest.raises(ValidationError):
        CapabilityExecutionRecord(
            capability_id="CAP-TEST-0001",
            status="success",
            execution_mode="shadow",
            affects_decision=False,
            duration_ms=-1,
        )


def test_affects_decision_must_remain_false():
    with pytest.raises(ValidationError):
        CapabilityExecutionRecord(
            capability_id="CAP-TEST-0001",
            status="success",
            execution_mode="shadow",
            affects_decision=True,
            duration_ms=1,
        )


def test_execution_mode_must_be_shadow():
    with pytest.raises(ValidationError):
        CapabilityExecutionRecord(
            capability_id="CAP-TEST-0001",
            status="success",
            execution_mode="runtime",
            affects_decision=False,
            duration_ms=1,
        )


def test_extra_fields_rejected():
    with pytest.raises(ValidationError):
        CapabilityExecutionRecord(
            capability_id="CAP-TEST-0001",
            status="success",
            execution_mode="shadow",
            affects_decision=False,
            duration_ms=1,
            unexpected=True,
        )


def test_invalid_capability_id_rejected():
    with pytest.raises(ValidationError):
        CapabilityExecutionRecord(
            capability_id="candidate",
            status="success",
            execution_mode="shadow",
            affects_decision=False,
            duration_ms=1,
        )