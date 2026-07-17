from app.capabilities import (
    CapabilityRequest,
)
from app.capabilities.knowledge_relevance.capability import (
    KNOWLEDGE_RELEVANCE_CAPABILITY_ID,
    KnowledgeRelevanceCapability,
)
from app.capabilities.knowledge_relevance.capability_manifest import (
    KNOWLEDGE_RELEVANCE_CAPABILITY_MANIFEST,
)
from app.capabilities.registry import (
    CapabilityRegistry,
)
from app.capabilities.runtime import (
    CapabilityRuntime,
)
from app.capabilities.knowledge_relevance.contracts import (
    KnowledgeRelevanceResult,
)
from app.knowledge.bootstrap import (
    build_default_registry,
)


def build_runtime():
    registry = CapabilityRegistry()

    registry.register(
        capability=KnowledgeRelevanceCapability(
            registry=build_default_registry(),
        ),
        manifest=KNOWLEDGE_RELEVANCE_CAPABILITY_MANIFEST,
    )

    return CapabilityRuntime(
        registry=registry,
    )


def build_request():
    return CapabilityRequest(
        request_id="REQ-KR-0001",
        payload={
            "domain": "transformer",
            "asset_type": "power_transformer",
            "available_evidence": (
                "COMTRADE waveform",
            ),
            "missing_evidence": (),
            "investigation_stage": (
                "hypothesis_evaluation"
            ),
            "max_results": 2,
        },
        context={
            "execution_mode": "shadow",
        },
    )


def test_runtime_executes_capability():
    runtime = build_runtime()

    execution = runtime.invoke(
        capability_id=KNOWLEDGE_RELEVANCE_CAPABILITY_ID,
        request=build_request(),
    )

    assert execution.error is None
    assert execution.result.status == "success"


def test_output_contains_reference_only_result():
    runtime = build_runtime()

    execution = runtime.invoke(
        capability_id=KNOWLEDGE_RELEVANCE_CAPABILITY_ID,
        request=build_request(),
    )

    result = KnowledgeRelevanceResult(
        **execution.result.output[
            "knowledge_relevance_result"
        ]
    )

    assert len(result.selected_ids) == 2
    assert "definition" not in execution.result.output
    assert execution.result.affects_decision is False


def test_capability_runs_in_shadow_mode():
    runtime = build_runtime()

    execution = runtime.invoke(
        capability_id=KNOWLEDGE_RELEVANCE_CAPABILITY_ID,
        request=build_request(),
    )

    assert execution.audit["shadow_only"] is True
