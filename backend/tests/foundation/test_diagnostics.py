from app.foundation.diagnostics import EngineDiagnostics


def test_engine_diagnostics_defaults():
    diagnostics = EngineDiagnostics()

    assert diagnostics.processed_items == 0
    assert diagnostics.execution_time_ms == 0.0
    assert diagnostics.warnings == ()
    assert diagnostics.errors == ()