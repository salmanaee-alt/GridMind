import pytest

from app.capabilities.knowledge.contracts import (
    CandidateSource,
    KnowledgeCandidateResult,
)
from app.capabilities.knowledge.generator import (
    KnowledgeCandidateGenerator,
)
from app.knowledge.bootstrap import (
    build_default_registry,
)
from app.knowledge.registry import (
    EngineeringKnowledgeRegistry,
)
from app.knowledge.transformer import (
    INTERNAL_TRANSFORMER_FAULT,
    MAGNETIZING_INRUSH,
)


def test_generator_accepts_registry_dependency():
    registry = build_default_registry()

    generator = KnowledgeCandidateGenerator(
        registry=registry,
    )

    assert generator.registry is registry


def test_generator_selects_candidates_by_domain():
    generator = KnowledgeCandidateGenerator(
        registry=build_default_registry(),
    )

    result = generator.generate(
        domain="transformer",
    )

    assert isinstance(
        result,
        KnowledgeCandidateResult,
    )
    assert result.candidate_count == 3
    assert tuple(
        item.knowledge_id
        for item in result.candidates
    ) == (
        "TR-EKO-0001",
        "TR-EKO-0002",
        "TR-EKO-0003",
    )


def test_generator_preserves_registry_order():
    registry = EngineeringKnowledgeRegistry(
        (
            MAGNETIZING_INRUSH,
            INTERNAL_TRANSFORMER_FAULT,
        )
    )

    generator = KnowledgeCandidateGenerator(
        registry=registry,
    )

    result = generator.generate(
        domain="transformer",
    )

    assert tuple(
        item.knowledge_id
        for item in result.candidates
    ) == (
        "TR-EKO-0002",
        "TR-EKO-0001",
    )


def test_generator_returns_empty_result_for_unknown_domain():
    generator = KnowledgeCandidateGenerator(
        registry=build_default_registry(),
    )

    result = generator.generate(
        domain="generator",
    )

    assert result.candidates == ()
    assert result.candidate_count == 0
    assert result.shadow_only is True
    assert result.affects_decision is False


def test_generator_candidates_are_registry_sourced():
    generator = KnowledgeCandidateGenerator(
        registry=build_default_registry(),
    )

    result = generator.generate(
        domain="transformer",
    )

    assert all(
        item.source == CandidateSource.REGISTRY
        for item in result.candidates
    )


def test_generator_uses_domain_match_reason():
    generator = KnowledgeCandidateGenerator(
        registry=build_default_registry(),
    )

    result = generator.generate(
        domain="transformer",
    )

    assert all(
        item.reason.code == "domain_match"
        for item in result.candidates
    )
    assert all(
        "transformer" in item.reason.description.lower()
        for item in result.candidates
    )


def test_generator_does_not_mutate_registry():
    registry = build_default_registry()
    before = registry.all()

    generator = KnowledgeCandidateGenerator(
        registry=registry,
    )

    generator.generate(
        domain="transformer",
    )

    assert registry.all() == before


def test_generator_returns_new_result_each_time():
    generator = KnowledgeCandidateGenerator(
        registry=build_default_registry(),
    )

    first = generator.generate(
        domain="transformer",
    )
    second = generator.generate(
        domain="transformer",
    )

    assert first is not second
    assert first == second


def test_generator_rejects_non_registry_dependency():
    with pytest.raises(
        TypeError,
        match="EngineeringKnowledgeRegistry",
    ):
        KnowledgeCandidateGenerator(
            registry=(),
        )


@pytest.mark.parametrize(
    "invalid_domain",
    [
        "",
        "   ",
        "Transformer",
        "transformer domain",
        "transformer/domain",
    ],
)
def test_generator_rejects_invalid_domain(
    invalid_domain: str,
):
    generator = KnowledgeCandidateGenerator(
        registry=build_default_registry(),
    )

    with pytest.raises(
        ValueError,
        match="domain",
    ):
        generator.generate(
            domain=invalid_domain,
        )


def test_generator_does_not_filter_by_category_or_status():
    generator = KnowledgeCandidateGenerator(
        registry=build_default_registry(),
    )

    result = generator.generate(
        domain="transformer",
    )

    expected_ids = tuple(
        item.knowledge_id
        for item in build_default_registry().by_domain(
            "transformer"
        )
    )

    assert tuple(
        item.knowledge_id
        for item in result.candidates
    ) == expected_ids


def test_generator_result_remains_shadow_only():
    generator = KnowledgeCandidateGenerator(
        registry=build_default_registry(),
    )

    result = generator.generate(
        domain="transformer",
    )

    assert result.shadow_only is True
    assert result.affects_decision is False
    assert all(
        item.shadow_only is True
        and item.affects_decision is False
        for item in result.candidates
    )
