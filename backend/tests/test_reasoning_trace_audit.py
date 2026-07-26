from app.brain.reasoning_trace_audit import (
    build_reasoning_trace_audit,
)


def _complete_trace():
    return [
        {"stage": "observe"},
        {"stage": "understand"},
        {"stage": "validate"},
        {"stage": "hypothesize"},
        {"stage": "reason"},
        {"stage": "evaluate"},
        {"stage": "decide"},
        {"stage": "explain"},
        {"stage": "learn"},
    ]


def test_complete_reasoning_trace_is_valid():
    audit = build_reasoning_trace_audit(
        _complete_trace()
    )

    assert audit["status"] == "complete"
    assert audit["trace_complete"] is True
    assert audit["missing_stages"] == []
    assert audit["duplicate_stages"] == []
    assert audit["unknown_stages"] == []
    assert audit["order_valid"] is True


def test_missing_stage_is_detected():
    steps = _complete_trace()
    steps = [
        step
        for step in steps
        if step["stage"] != "evaluate"
    ]

    audit = build_reasoning_trace_audit(steps)

    assert audit["status"] == "incomplete"
    assert audit["trace_complete"] is False
    assert audit["missing_stages"] == ["evaluate"]


def test_duplicate_stage_is_detected():
    steps = _complete_trace()
    steps.insert(
        5,
        {"stage": "reason"},
    )

    audit = build_reasoning_trace_audit(steps)

    assert audit["status"] == "incomplete"
    assert audit["trace_complete"] is False
    assert audit["duplicate_stages"] == ["reason"]


def test_wrong_order_is_detected():
    steps = _complete_trace()

    steps[4], steps[5] = (
        steps[5],
        steps[4],
    )

    audit = build_reasoning_trace_audit(steps)

    assert audit["status"] == "incomplete"
    assert audit["trace_complete"] is False
    assert audit["order_valid"] is False


def test_reasoning_trace_audit_is_audit_only():
    audit = build_reasoning_trace_audit(
        _complete_trace()
    )

    assert audit["affects_confidence"] is False
    assert audit["affects_ranking"] is False
    assert audit["affects_decision"] is False
    