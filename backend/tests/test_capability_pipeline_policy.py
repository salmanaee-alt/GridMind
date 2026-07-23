import pytest
from pydantic import ValidationError

from app.capabilities.pipeline import (
    CapabilityPipelinePolicy,
    CapabilityPipelineStep,
)


def test_valid_capability_pipeline_policy() -> None:
    policy = CapabilityPipelinePolicy(
        pipeline_id="transformer-knowledge",
        version="0.27.0",
        steps=(
            CapabilityPipelineStep(
                capability_id="CAP-KNOWLEDGE-0001",
            ),
            CapabilityPipelineStep(
                capability_id="CAP-RELEVANCE-0001",
                depends_on=("CAP-KNOWLEDGE-0001",),
            ),
        ),
    )

    assert policy.pipeline_id == "transformer-knowledge"
    assert policy.version == "0.27.0"
    assert len(policy.steps) == 2


def test_pipeline_step_defaults_to_shadow() -> None:
    step = CapabilityPipelineStep(
        capability_id="CAP-KNOWLEDGE-0001",
    )

    assert step.execution_mode == "shadow"
    assert step.required is True
    assert step.depends_on == ()


def test_pipeline_step_rejects_non_shadow_mode() -> None:
    with pytest.raises(ValidationError):
        CapabilityPipelineStep(
            capability_id="CAP-KNOWLEDGE-0001",
            execution_mode="active",
        )


def test_pipeline_step_rejects_invalid_capability_id() -> None:
    with pytest.raises(ValidationError):
        CapabilityPipelineStep(
            capability_id="invalid-id",
        )


def test_pipeline_policy_rejects_invalid_version() -> None:
    with pytest.raises(ValidationError):
        CapabilityPipelinePolicy(
            pipeline_id="transformer-knowledge",
            version="v0.27",
        )


def test_pipeline_policy_rejects_extra_fields() -> None:
    with pytest.raises(ValidationError):
        CapabilityPipelinePolicy(
            pipeline_id="transformer-knowledge",
            version="0.27.0",
            unexpected=True,
        )