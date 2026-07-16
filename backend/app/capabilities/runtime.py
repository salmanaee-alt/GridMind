from __future__ import annotations

from time import perf_counter
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.capabilities.contracts import (
    CapabilityRequest,
    CapabilityResult,
)
from app.capabilities.errors import (
    CapabilityError,
)
from app.capabilities.registry import (
    CapabilityRegistry,
)


class CapabilityExecution(BaseModel):
    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
    )

    result: CapabilityResult
    audit: dict[str, Any] = Field(
        default_factory=dict,
    )
    duration_ms: float = Field(
        ge=0,
    )
    error: CapabilityError | None = None


class CapabilityRuntime:
    def __init__(
        self,
        *,
        registry: CapabilityRegistry,
    ) -> None:
        if not isinstance(
            registry,
            CapabilityRegistry,
        ):
            raise TypeError(
                "CapabilityRuntime requires a "
                "CapabilityRegistry."
            )

        self._registry = registry

    def invoke(
        self,
        *,
        capability_id: str,
        request: CapabilityRequest,
    ) -> CapabilityExecution:
        started_at = perf_counter()

        registration = self._registry.get(
            capability_id
        )

        if registration is None:
            return self._error_execution(
                capability_id=capability_id,
                request_id=request.request_id,
                error_type="not_found",
                message=(
                    f"Capability {capability_id!r} "
                    "is not registered."
                ),
                stage="runtime",
                retryable=False,
                started_at=started_at,
            )

        capability = registration.capability
        metadata = capability.metadata()

        execution_mode = request.context.get(
            "execution_mode"
        )

        if (
            metadata.shadow_only
            and execution_mode != "shadow"
        ):
            return self._error_execution(
                capability_id=capability_id,
                request_id=request.request_id,
                error_type="shadow_mode_required",
                message=(
                    "Capability requires shadow execution mode."
                ),
                stage="runtime",
                retryable=False,
                started_at=started_at,
            )

        try:
            capability.validate(request)
        except Exception as exc:
            return self._error_execution(
                capability_id=capability_id,
                request_id=request.request_id,
                error_type="validation_error",
                message=str(exc),
                stage="validate",
                retryable=False,
                started_at=started_at,
            )

        try:
            result = capability.execute(request)
        except Exception as exc:
            return self._error_execution(
                capability_id=capability_id,
                request_id=request.request_id,
                error_type="execution_error",
                message=str(exc),
                stage="execute",
                retryable=False,
                started_at=started_at,
            )

        if result.capability_id != capability_id:
            return self._error_execution(
                capability_id=capability_id,
                request_id=request.request_id,
                error_type="result_integrity_error",
                message=(
                    "Capability result capability_id does not "
                    "match the invoked capability."
                ),
                stage="runtime",
                retryable=False,
                started_at=started_at,
            )

        if result.affects_decision is not False:
            return self._error_execution(
                capability_id=capability_id,
                request_id=request.request_id,
                error_type="result_integrity_error",
                message=(
                    "Capability result must not affect decisions."
                ),
                stage="runtime",
                retryable=False,
                started_at=started_at,
            )

        try:
            audit = capability.audit(result)
        except Exception as exc:
            return self._error_execution(
                capability_id=capability_id,
                request_id=request.request_id,
                error_type="audit_error",
                message=str(exc),
                stage="audit",
                retryable=False,
                started_at=started_at,
            )

        return CapabilityExecution(
            result=result,
            audit=audit,
            duration_ms=self._duration_ms(
                started_at
            ),
            error=None,
        )

    def _error_execution(
        self,
        *,
        capability_id: str,
        request_id: str,
        error_type: str,
        message: str,
        stage: str,
        retryable: bool,
        started_at: float,
    ) -> CapabilityExecution:
        return CapabilityExecution(
            result=CapabilityResult(
                capability_id=capability_id,
                status="error",
                output={},
                audit={},
                affects_decision=False,
            ),
            audit={},
            duration_ms=self._duration_ms(
                started_at
            ),
            error=CapabilityError(
                error_type=error_type,
                message=message,
                capability_id=capability_id,
                request_id=request_id,
                stage=stage,
                retryable=retryable,
            ),
        )

    @staticmethod
    def _duration_ms(
        started_at: float,
    ) -> float:
        return round(
            max(
                0.0,
                (
                    perf_counter()
                    - started_at
                )
                * 1000,
            ),
            3,
        )
