import pytest

from app.capabilities.knowledge_relevance.manifest import (
    KNOWLEDGE_RELEVANCE_MANIFEST,
)


def test_manifest_identity():
    assert (
        KNOWLEDGE_RELEVANCE_MANIFEST.capability_id
        == "knowledge_relevance"
    )
    assert (
        KNOWLEDGE_RELEVANCE_MANIFEST.name
        == "Knowledge Relevance Engine"
    )
    assert KNOWLEDGE_RELEVANCE_MANIFEST.version == "2.0.0"


def test_manifest_is_experimental_shadow_only():
    assert KNOWLEDGE_RELEVANCE_MANIFEST.status == "experimental"
    assert KNOWLEDGE_RELEVANCE_MANIFEST.shadow_only is True
    assert KNOWLEDGE_RELEVANCE_MANIFEST.affects_decision is False


def test_manifest_declares_contracts():
    assert (
        KNOWLEDGE_RELEVANCE_MANIFEST.request_model
        == "KnowledgeRelevanceRequest"
    )
    assert (
        KNOWLEDGE_RELEVANCE_MANIFEST.result_model
        == "KnowledgeRelevanceResult"
    )


def test_manifest_has_clear_responsibility():
    description = (
        KNOWLEDGE_RELEVANCE_MANIFEST.description.lower()
    )

    assert "rank" in description
    assert "knowledge" in description
    assert "search" not in description
    assert "rag" not in description
    assert "embedding" not in description


@pytest.mark.parametrize(
    "forbidden_capability",
    [
        "execution_authority",
        "decision_authority",
        "control_authority",
    ],
)
def test_manifest_does_not_claim_authority(
    forbidden_capability: str,
):
    assert forbidden_capability not in (
        KNOWLEDGE_RELEVANCE_MANIFEST.capabilities
    )
