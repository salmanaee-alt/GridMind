from __future__ import annotations

import multiprocessing
from queue import Empty
from time import perf_counter
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.capabilities.base import (
    EngineeringCapability,
)
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


def _run_capability_worker(
    capability: EngineeringCapability,
    capability_id: str,
    request: CapabilityRequest,
    result_queue: Any,
) -> None:
    try:
        capability.validate(request)
    except Exception as exc:
        result_queue.put({
            "kind": "error",
            "error_type": "validation_error",
            "message": str(exc),
            "stage": "validate",
            "retryable": False,
        })
        return

    try:
        result = capability.execute(request)
    except Exception as exc:
        result_queue.put({
            "kind": "error",
            "error_type": "execution_error",
            "message": str(exc),
            "stage": "execute",
            "retryable": False,
        })
        return

    if result.capability_id != capability_id:
        result_queue.put({
            "kind": "error",
            "error_type": "result_integrity_error",
            "message": (
                "Capability result capability_id does not "
                "match the invoked capability."
            ),
            "stage": "runtime",
            "retryable": False,
        })
        return

    if result.affects_decision is not False:
        result_queue.put({
            "kind": "error",
            "error_type": "result_integrity_error",
            "message": (
                "Capability result must not affect decisions."
            ),
            "stage": "runtime",
            "retryable": False,
        })
        return

    try:
        audit = capability.audit(result)
    except Exception as exc:
        result_queue.put({
            "kind": "error",
            "error_type": "audit_error",
            "message": str(exc),
            "stage": "audit",
            "retryable": False,
        })
        return

    result_queue.put({
        "kind": "success",
        "result": result.model_dump(),
        "audit": audit,
    })


class CapabilityRuntime:
    def __init__(
        self,
        *,
        registry: CapabilityRegistry,
        timeout_seconds: float | None = None,
        process_isolation: bool = False,
    ) -> None:
        if not isinstance(
            registry,
            CapabilityRegistry,
        ):
            raise TypeError(
                "CapabilityRuntime requires a "
                "CapabilityRegistry."
            )

        if timeout_seconds is not None:
            if (
                not isinstance(
                    timeout_seconds,
                    (int, float),
                )
                or isinstance(timeout_seconds, bool)
                or timeout_seconds <= 0
            ):
                raise ValueError(
                    "timeout_seconds must be greater than zero."
                )

        if not isinstance(process_isolation, bool):
            raise TypeError(
                "process_isolation must be a boolean."
            )

        if process_isolation and timeout_seconds is None:
            raise ValueError(
                "Process isolation requires timeout_seconds."
            )

        self._registry = registry
        self._timeout_seconds = (
            float(timeout_seconds)
            if timeout_seconds is not None
            else None
        )
        self._process_isolation = process_isolation

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

        if self._process_isolation:
            return self._invoke_isolated(
                capability=capability,
                capability_id=capability_id,
                request=request,
                started_at=started_at,
            )

        return self._invoke_in_process(
            capability=capability,
            capability_id=capability_id,
            request=request,
            started_at=started_at,
        )

    def _invoke_in_process(
        self,
        *,
        capability: EngineeringCapability,
        capability_id: str,
        request: CapabilityRequest,
        started_at: float,
    ) -> CapabilityExecution:
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

        integrity_error = self._validate_result_integrity(
            capability_id=capability_id,
            result=result,
        )

        if integrity_error is not None:
            return self._error_execution(
                capability_id=capability_id,
                request_id=request.request_id,
                error_type="result_integrity_error",
                message=integrity_error,
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

    def _invoke_isolated(
        self,
        *,
        capability: EngineeringCapability,
        capability_id: str,
        request: CapabilityRequest,
        started_at: float,
    ) -> CapabilityExecution:
        context = multiprocessing.get_context(
            "fork"
        )
        result_queue = context.Queue(
            maxsize=1
        )
        process = context.Process(
            target=_run_capability_worker,
            args=(
                capability,
                capability_id,
                request,
                result_queue,
            ),
            daemon=True,
        )

        process.start()
        process.join(
            self._timeout_seconds
        )

        if process.is_alive():
            process.terminate()
            process.join()

            result_queue.close()
            result_queue.join_thread()

            return self._error_execution(
                capability_id=capability_id,
                request_id=request.request_id,
                error_type="timeout_error",
                message=(
                    "Capability execution exceeded "
                    f"{self._timeout_seconds} seconds."
                ),
                stage="execute",
                retryable=True,
                started_at=started_at,
            )

        try:
            worker_output = result_queue.get(
                timeout=0.2,
            )
        except Empty:
            result_queue.close()
            result_queue.join_thread()

            return self._error_execution(
                capability_id=capability_id,
                request_id=request.request_id,
                error_type="worker_error",
                message=(
                    "Capability worker exited without "
                    "returning a result."
                ),
                stage="runtime",
                retryable=True,
                started_at=started_at,
            )

        result_queue.close()
        result_queue.join_thread()

        if worker_output["kind"] == "error":
            return self._error_execution(
                capability_id=capability_id,
                request_id=request.request_id,
                error_type=worker_output[
                    "error_type"
                ],
                message=worker_output["message"],
                stage=worker_output["stage"],
                retryable=worker_output["retryable"],
                started_at=started_at,
            )

        result = CapabilityResult(
            **worker_output["result"]
        )

        return CapabilityExecution(
            result=result,
            audit=worker_output["audit"],
            duration_ms=self._duration_ms(
                started_at
            ),
            error=None,
        )

    @staticmethod
    def _validate_result_integrity(
        *,
        capability_id: str,
        result: CapabilityResult,
    ) -> str | None:
        if result.capability_id != capability_id:
            return (
                "Capability result capability_id does not "
                "match the invoked capability."
            )

        if result.affects_decision is not False:
            return (
                "Capability result must not affect decisions."
            )

        return None

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
