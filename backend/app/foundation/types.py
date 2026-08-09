from __future__ import annotations

from enum import Enum


class ExecutionStatus(str, Enum):
    """
    Unified execution status returned by every Foundation engine.
    """

    SUCCESS = "success"

    FAILED = "failed"

    PARTIAL = "partial"

    SKIPPED = "skipped"