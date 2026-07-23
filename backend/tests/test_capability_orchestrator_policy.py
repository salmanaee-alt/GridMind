from unittest.mock import Mock

import pytest

from app.capabilities.pipeline import (
    CapabilityPipelinePolicy,
    CapabilityPipelineStep,
)
from app.capabilities.orchestrator import CapabilityOrchestrator


def test_execute_policy_preserves_step_order() -> None:
    runtime = Mock()

    first_execution = Mock()
    second_execution = Mock()

    runtime.invoke.side_effect = [
        first_execution,
        second_execution,
    ]

    orchestrator = CapabilityOrchestrator(
        runtime=runtime,
    )

    policy = CapabilityPipelinePolicy(
        pipeline_id="test-pipeline",
        version="0.27.0",
        steps=(
            CapabilityPipelineStep(
                capability_id="CAP-FIRST-0001",
            ),
            CapabilityPipelineStep(
                capability_id="CAP-SECOND-0001",
                depends_on=("CAP-FIRST-0001",),
            ),
        ),
    )

    first_request = object()
    second_request = object()

    results = orchestrator.execute_policy(
        policy=policy,
        requests={
            "CAP-FIRST-0001": first_request,
            "CAP-SECOND-0001": second_request,
        },
    )

    assert results == [
        first_execution,
        second_execution,
    ]

    assert runtime.invoke.call_args_list[0].kwargs == {
        "capability_id": "CAP-FIRST-0001",
        "request": first_request,
    }

    assert runtime.invoke.call_args_list[1].kwargs == {
        "capability_id": "CAP-SECOND-0001",
        "request": second_request,
    }


def test_execute_policy_rejects_missing_required_request() -> None:
    runtime = Mock()

    orchestrator = CapabilityOrchestrator(
        runtime=runtime,
    )

    policy = CapabilityPipelinePolicy(
        pipeline_id="test-pipeline",
        version="0.27.0",
        steps=(
            CapabilityPipelineStep(
                capability_id="CAP-REQUIRED-0001",
            ),
        ),
    )

    with pytest.raises(
        ValueError,
        match="Required capability request missing",
    ):
        orchestrator.execute_policy(
            policy=policy,
            requests={},
        )

    runtime.invoke.assert_not_called()


def test_execute_policy_skips_missing_optional_request() -> None:
    runtime = Mock()

    orchestrator = CapabilityOrchestrator(
        runtime=runtime,
    )

    policy = CapabilityPipelinePolicy(
        pipeline_id="test-pipeline",
        version="0.27.0",
        steps=(
            CapabilityPipelineStep(
                capability_id="CAP-OPTIONAL-0001",
                required=False,
            ),
        ),
    )

    results = orchestrator.execute_policy(
        policy=policy,
        requests={},
    )

    assert results == []
    runtime.invoke.assert_not_called()


def test_execute_policy_enforces_dependencies() -> None:
    runtime = Mock()

    orchestrator = CapabilityOrchestrator(
        runtime=runtime,
    )

    policy = CapabilityPipelinePolicy(
        pipeline_id="test-pipeline",
        version="0.27.0",
        steps=(
            CapabilityPipelineStep(
                capability_id="CAP-SECOND-0001",
                depends_on=("CAP-FIRST-0001",),
            ),
        ),
    )

    with pytest.raises(
        ValueError,
        match="Capability dependency not satisfied",
    ):
        orchestrator.execute_policy(
            policy=policy,
            requests={
                "CAP-SECOND-0001": object(),
            },
        )

    runtime.invoke.assert_not_called()