from app.capabilities.knowledge_relevance.runtime import (
    execute_knowledge_relevance,
)
from app.capabilities.knowledge_relevance import (
    KnowledgeRelevanceRequest,
)
from app.knowledge.bootstrap import (
    build_default_registry,
)
from app.knowledge.registry import (
    EngineeringKnowledgeRegistry,
)


def build_request():
    return KnowledgeRelevanceRequest(
        domain="transformer",
        asset_type="power_transformer",
        available_evidence=(
            "COMTRADE waveform",
        ),
        missing_evidence=(),
        investigation_stage="hypothesis_evaluation",
        max_results=2,
    )


def test_runtime_returns_ranked_result():
    result = execute_knowledge_relevance(
        registry=build_default_registry(),
        request=build_request(),
    )

    assert len(result.selected_ids) == 2
    assert len(result.scores) == 2


def test_runtime_excludes_deprecated_knowledge():
    source = build_default_registry().all()[0]

    active = source.model_copy(
        update={
            "knowledge_id": "ACTIVE-EKO-0001",
            "status": "active",
        }
    )
    deprecated = source.model_copy(
        update={
            "knowledge_id": "DEPRECATED-EKO-0001",
            "status": "deprecated",
        }
    )

    registry = EngineeringKnowledgeRegistry()
    registry.register(active)
    registry.register(deprecated)

    result = execute_knowledge_relevance(
        registry=registry,
        request=build_request(),
    )

    assert "ACTIVE-EKO-0001" in result.selected_ids
    assert "DEPRECATED-EKO-0001" not in result.selected_ids
    assert "DEPRECATED-EKO-0001" not in result.ignored_ids


def test_runtime_returns_reference_only():
    result = execute_knowledge_relevance(
        registry=build_default_registry(),
        request=build_request(),
    )

    dumped = result.model_dump()

    assert "definition" not in dumped
    assert "references" not in dumped
    assert "content" not in dumped
