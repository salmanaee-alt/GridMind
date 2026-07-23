from __future__ import annotations

from collections.abc import Iterable, Mapping

from app.capabilities.pipeline import (
    CapabilityPipelinePolicy,
)
from app.capabilities.runtime import (
    CapabilityExecution,
    CapabilityRuntime,
)


class CapabilityOrchestrator:
    """
    Executes capabilities in deterministic order.

    This class contains orchestration behavior only.
    It contains no engineering reasoning and
    no decision-making logic.
    """

    def __init__(
        self,
        runtime: CapabilityRuntime,
    ) -> None:
        self._runtime = runtime

    def execute(
        self,
        executions: Iterable[tuple[str, object]],
    ) -> list[CapabilityExecution]:
        """
        Preserve the existing explicit execution path.
        """

        results: list[CapabilityExecution] = []

        for capability_id, request in executions:
            results.append(
                self._runtime.invoke(
                    capability_id=capability_id,
                    request=request,
                )
            )

        return results

    def execute_policy(
        self,
        policy: CapabilityPipelinePolicy,
        requests: Mapping[str, object],
    ) -> list[CapabilityExecution]:
        """
        Execute requests according to pipeline policy.

        The policy controls orchestration only:
        - deterministic order
        - required/optional execution
        - dependency ordering

        It cannot affect engineering decisions.
        """

        results: list[CapabilityExecution] = []
        completed: set[str] = set()

        for step in policy.steps:
            missing_dependencies = [
                dependency
                for dependency in step.depends_on
                if dependency not in completed
            ]

            if missing_dependencies:
                raise ValueError(
                    "Capability dependency not satisfied: "
                    f"{step.capability_id} depends on "
                    f"{missing_dependencies}"
                )

            request = requests.get(step.capability_id)

            if request is None:
                if step.required:
                    raise ValueError(
                        "Required capability request missing: "
                        f"{step.capability_id}"
                    )

                continue

            results.append(
                self._runtime.invoke(
                    capability_id=step.capability_id,
                    request=request,
                )
            )

            completed.add(step.capability_id)

        return results
    