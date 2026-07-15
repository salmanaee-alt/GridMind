from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from app.capabilities.contracts import (
    CapabilityMetadata,
    CapabilityRequest,
    CapabilityResult,
)


class EngineeringCapability(ABC):
    @abstractmethod
    def metadata(self) -> CapabilityMetadata:
        """Return the immutable capability metadata contract."""

    @abstractmethod
    def validate(
        self,
        request: CapabilityRequest,
    ) -> None:
        """Validate a request without mutating it."""

    @abstractmethod
    def execute(
        self,
        request: CapabilityRequest,
    ) -> CapabilityResult:
        """Execute the capability and return a descriptive result."""

    @abstractmethod
    def audit(
        self,
        result: CapabilityResult,
    ) -> dict[str, Any]:
        """Return audit metadata for the capability result."""
