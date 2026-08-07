from __future__ import annotations

from typing import Any

from app.thinking.contracts import (
    ThinkingStage,
    ThinkingState,
)


def _extract_status(
    check: Any,
) -> str | None:
    if not isinstance(check, dict):
        return None

    value = check.get("status")

    if isinstance(value, str):
        return value.strip().lower()

    return None


class VerifyPhysicsProcessor:
    stage = ThinkingStage.VERIFY_PHYSICS

    def execute(
        self,
        state: ThinkingState,
    ) -> ThinkingState:
        valid_count = 0
        invalid_count = 0
        unknown_count = 0

        for check in state.physics_checks:
            status = _extract_status(check)

            if status == "valid":
                valid_count += 1
            elif status == "invalid":
                invalid_count += 1
            else:
                unknown_count += 1

        check_count = len(
            state.physics_checks
        )

        if check_count == 0:
            verification_status = (
                "not_available"
            )
        elif invalid_count > 0:
            verification_status = (
                "physics_conflict"
            )
        elif unknown_count > 0:
            verification_status = (
                "incomplete"
            )
        else:
            verification_status = (
                "verified"
            )

        return state.model_copy(
            update={
                "metadata": {
                    **state.metadata,
                    "verify_physics_stage": {
                        "check_count": check_count,
                        "valid_count": valid_count,
                        "invalid_count": (
                            invalid_count
                        ),
                        "unknown_count": (
                            unknown_count
                        ),
                        "verification_status": (
                            verification_status
                        ),
                    },
                }
            }
        )