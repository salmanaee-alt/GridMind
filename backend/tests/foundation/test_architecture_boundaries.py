from __future__ import annotations

from pathlib import Path


FORBIDDEN_IMPORTS = (
    "app.brain",
    "app.thinking",
    "app.reasoning",
    "app.knowledge",
    "app.transformer",
    "app.protection",
    "app.capabilities",
)


def test_foundation_has_no_forbidden_dependencies():
    foundation_path = Path(
        "app/foundation"
    )

    python_files = tuple(
        foundation_path.glob("*.py")
    )

    assert python_files

    violations: list[str] = []

    for file_path in python_files:
        content = file_path.read_text(
            encoding="utf-8"
        )

        for forbidden_import in FORBIDDEN_IMPORTS:
            if forbidden_import in content:
                violations.append(
                    f"{file_path}: {forbidden_import}"
                )

    assert violations == []


def test_foundation_adapters_do_not_import_each_other():
    capability_adapter = Path(
        "app/capabilities/foundation_adapter.py"
    ).read_text(
        encoding="utf-8"
    )

    thinking_adapter_path = Path(
        "app/thinking/foundation_adapter.py"
    )

    assert "app.thinking" not in capability_adapter

    if thinking_adapter_path.exists():
        thinking_adapter = (
            thinking_adapter_path.read_text(
                encoding="utf-8"
            )
        )

        assert (
            "app.capabilities"
            not in thinking_adapter
        )