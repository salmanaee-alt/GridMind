from __future__ import annotations

from typing import Any

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)

from app.foundation.context import (
    ExecutionContext,
)


class ExecutionContextValidation(BaseModel):
    """
    Validation result for an ExecutionContext.
    """

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
    )

    valid: bool

    errors: tuple[str, ...] = ()

    warnings: tuple[str, ...] = ()

    metadata: dict[str, Any] = Field(
        default_factory=dict,
    )


class ExecutionContextValidator:
    """
    Stateless validator for ExecutionContext.
    """

    def validate(
        self,
        context: ExecutionContext,
    ) -> ExecutionContextValidation:

        errors: list[str] = []
        warnings: list[str] = []

        if not context.correlation_id.strip():
            errors.append(
                "correlation_id is required"
            )

        if not context.resources:
            warnings.append(
                "execution context has no resources"
            )

        return ExecutionContextValidation(
            valid=not errors,
            errors=tuple(errors),
            warnings=tuple(warnings),
        )


def validate_context(
    context,
) -> bool:

    return context.session is not None