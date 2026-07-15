from __future__ import annotations

from typing import Literal

from pydantic import (
    Field,
    field_validator,
    model_validator,
)

from app.capabilities.contracts import (
    CAPABILITY_ABI_VERSION,
    FrozenCapabilityModel,
)


CapabilityManifestStatus = Literal[
    "experimental",
    "reviewed",
    "approved",
    "deprecated",
]


class CapabilityManifest(FrozenCapabilityModel):
    capability_id: str = Field(
        pattern=r"^CAP-[A-Z0-9]{2,20}-[0-9]{4,}$"
    )
    name: str = Field(
        min_length=1,
        max_length=200,
    )
    version: str = Field(
        pattern=r"^[0-9]+\.[0-9]+\.[0-9]+$"
    )
    abi_version: str = Field(
        pattern=r"^[0-9]+\.[0-9]+$"
    )
    domain: str = Field(
        pattern=r"^[a-z][a-z0-9_]{1,63}$"
    )
    requires: tuple[str, ...] = ()
    produces: tuple[str, ...] = ()
    shadow_only: bool
    affects_decision: Literal[False] = False
    status: CapabilityManifestStatus
    author: str = Field(
        min_length=1,
        max_length=200,
    )

    @field_validator(
        "requires",
        "produces",
    )
    @classmethod
    def validate_contract_entries(
        cls,
        values: tuple[str, ...],
    ) -> tuple[str, ...]:
        normalized = tuple(
            value.strip()
            for value in values
        )

        if any(not value for value in normalized):
            raise ValueError(
                "Capability contract entries must not be blank."
            )

        if len(normalized) != len(set(normalized)):
            raise ValueError(
                "Capability requires and produces entries "
                "must be unique."
            )

        return normalized

    @model_validator(mode="after")
    def validate_abi_compatibility(
        self,
    ) -> "CapabilityManifest":
        if self.abi_version != CAPABILITY_ABI_VERSION:
            raise ValueError(
                "Capability ABI version is incompatible with "
                f"the current ABI {CAPABILITY_ABI_VERSION}."
            )

        return self
