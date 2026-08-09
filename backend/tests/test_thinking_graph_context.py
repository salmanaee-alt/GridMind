from app.thinking.graph_context import (
    ThinkingGraphContext,
)


def test_default_graph_context():
    context = ThinkingGraphContext()

    assert context.evidence_graph is None
    assert context.lineage_graph is None

    assert context.shadow_only is True
    assert context.affects_reasoning is False
    assert context.affects_decision is False


def test_graph_context_is_immutable():
    context = ThinkingGraphContext()

    try:
        context.shadow_only = False
        assert False
    except Exception:
        pass