from __future__ import annotations


class FoundationError(Exception):
    """
    Base exception for Foundation-layer failures.
    """


class EngineRegistrationError(
    FoundationError,
):
    """
    Raised when an engine cannot be registered.
    """


class EngineNotFoundError(
    FoundationError,
):
    """
    Raised when a requested engine does not exist.
    """


class ContextValidationError(
    FoundationError,
):
    """
    Raised when an execution context is invalid.
    """


class EngineExecutionError(
    FoundationError,
):
    """
    Raised when an engine execution fails.
    """