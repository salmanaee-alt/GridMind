from __future__ import annotations

from app.capabilities.contracts import (
    CapabilityMetadata,
    CapabilityRequest,
)
from app.capabilities.runtime import (
    CapabilityRuntime,
)
from app.foundation.context import (
    ExecutionContext,
)
from app.foundation.diagnostics import (
    EngineDiagnostics,
)
from app.foundation.metadata import (
    EngineMetadata,
)
from app.foundation.results import (
    EngineResult,
)
from app.foundation.types import (
    ExecutionStatus,
)


CAPABILITY_REQUEST_RESOURCE_KEY = (
    "capability_request"
)


class CapabilityFoundationAdapter:
    """
    Foundation adapter for one Capability Runtime invocation.

    This adapter is additive only.
    It does not replace CapabilityRuntime or CapabilityRegistry.
    """

    def __init__(
        self,
        *,
        capability_id: str,
        runtime: CapabilityRuntime,
        metadata: CapabilityMetadata,
    ) -> None:
        if not isinstance(
            capability_id,
            str,
        ) or not capability_id:
            raise ValueError(
                "capability_id must be a non-empty string."
            )

        if not isinstance(
            runtime,
            CapabilityRuntime,
        ):
            raise TypeError(
                "runtime must be a CapabilityRuntime."
            )

        if not isinstance(
            metadata,
            CapabilityMetadata,
        ):
            raise TypeError(
                "metadata must be CapabilityMetadata."
            )

        if metadata.capability_id != capability_id:
            raise ValueError(
                "metadata capability_id must match "
                "the adapter capability_id."
            )

        self._capability_id = capability_id
        self._runtime = runtime
        self._metadata = metadata

    @property
    def metadata(
        self,
    ) -> EngineMetadata:
        return EngineMetadata(
            name=(
                f"capability:"
                f"{self._metadata.capability_id}"
            ),
            version=self._metadata.version,
            description=self._metadata.name,
            category="capability",
            experimental=True,
        )

    def execute(
        self,
        context: ExecutionContext,
    ) -> EngineResult:
        request = context.resources.get(
            CAPABILITY_REQUEST_RESOURCE_KEY
        )

        if request is None:
            raise ValueError(
                "ExecutionContext.resources is missing "
                f"{CAPABILITY_REQUEST_RESOURCE_KEY!r}."
            )

        if not isinstance(
            request,
            CapabilityRequest,
        ):
            raise TypeError(
                f"{CAPABILITY_REQUEST_RESOURCE_KEY!r} "
                "must contain a CapabilityRequest."
            )

        execution = self._runtime.invoke(
            capability_id=self._capability_id,
            request=request,
        )

        native_result = execution.result

        if native_result.affects_decision is not False:
            raise ValueError(
                "Capability result violates the native "
                "safety contract."
            )

        status = self._map_status(
            native_result.status
        )

        diagnostic_metadata = {
            "capability_id":
                self._capability_id,
        }

        errors: tuple[str, ...] = ()

        if execution.error is not None:
            errors = (
                execution.error.message,
            )

            diagnostic_metadata.update(
                {
                    "error_type":
                        execution.error.error_type,
                    "retryable":
                        execution.error.retryable,
                    "stage":
                        execution.error.stage,
                }
            )

        result_metadata = {
            "capability_id":
                self._capability_id,
            "request_id":
                request.request_id,
        }

        if execution.audit:
            result_metadata["audit"] = (
                execution.audit
            )

        diagnostics = EngineDiagnostics(
            execution_time_ms=(
                execution.duration_ms
            ),
            errors=errors,
            traceability=(
                request.request_id,
            ),
            metadata=diagnostic_metadata,
        )

        return EngineResult(
            status=status,
            payload=native_result.output,
            diagnostics=diagnostics,
            metadata=result_metadata,
            execution_summary=(
                f"Capability {self._capability_id} "
                f"completed with status "
                f"{native_result.status}."
            ),
        )

    @staticmethod
    def _map_status(
        status: str,
    ) -> ExecutionStatus:
        if status == "success":
            return ExecutionStatus.SUCCESS

        if status == "skipped":
            return ExecutionStatus.SKIPPED

        return ExecutionStatus.FAILED