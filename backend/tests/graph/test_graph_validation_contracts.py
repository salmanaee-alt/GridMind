from app.graph.validation import (
    GraphValidation,
)


def test_creates_validation():
    validation = GraphValidation(
        valid=True,
    )

    assert validation.valid is True
    assert validation.duplicate_node_ids == ()
    assert validation.duplicate_edges == ()
    assert validation.cycles == ()
    assert validation.orphan_nodes == ()
    assert validation.affects_reasoning is False
    assert validation.affects_decision is False


def test_creates_invalid_validation():
    validation = GraphValidation(
        valid=False,
        duplicate_node_ids=("a",),
        missing_source_nodes=("b",),
        missing_target_nodes=("c",),
        orphan_nodes=("d",),
        duplicate_edges=("e",),
        cycles=(
            ("x", "y", "x"),
        ),
    )

    assert validation.valid is False
    assert validation.duplicate_node_ids == ("a",)
    assert validation.missing_source_nodes == ("b",)
    assert validation.missing_target_nodes == ("c",)
    assert validation.orphan_nodes == ("d",)
    assert validation.duplicate_edges == ("e",)